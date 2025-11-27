# ============================================================
# UNS VISA MANAGEMENT SYSTEM - Backend API
# FastAPI + PostgreSQL
# ============================================================

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
import asyncpg
import re
import os

# Import routers
try:
    from auth import router as auth_router
    from haken_saki import router as haken_saki_router
    from export import router as export_router
except ImportError:
    auth_router = None
    haken_saki_router = None
    export_router = None

app = FastAPI(
    title="UNS Visa Management API",
    description="API para gestión de visas de trabajadores派遣",
    version="1.0.0"
)

# Include routers
if auth_router:
    app.include_router(auth_router)
if haken_saki_router:
    app.include_router(haken_saki_router)
if export_router:
    app.include_router(export_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

from database import init_db, close_db, get_db_pool

# ... (imports)

# ============================================================
# CONFIGURACIÓN
# ============================================================

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

# ============================================================
# VALIDADORES
# ============================================================

class Validators:
    @staticmethod
    def residence_card(card: str) -> bool:
        """在留カード番号: 2文字 + 8数字 + 2文字 (例: AB12345678CD)"""
        return bool(re.match(r'^[A-Z]{2}\d{8}[A-Z]{2}$', card.upper())) if card else False
    
    @staticmethod
    def corporation_number(num: str) -> bool:
        """法人番号: 13桁"""
        return bool(re.match(r'^\d{13}$', num)) if num else True
    
    @staticmethod
    def insurance_number(num: str) -> bool:
        """雇用保険番号: 11桁"""
        return bool(re.match(r'^\d{11}$', num)) if num else True
    
    @staticmethod
    def phone_japan(phone: str) -> bool:
        """日本の電話番号"""
        if not phone:
            return True
        clean = re.sub(r'[-\s]', '', phone)
        return bool(re.match(r'^0\d{9,10}$', clean))
    
    @staticmethod
    def postal_code(code: str) -> bool:
        """郵便番号: 7桁"""
        if not code:
            return True
        clean = re.sub(r'[-\s]', '', code)
        return bool(re.match(r'^\d{7}$', clean))
    
    @staticmethod
    def visa_status(expiration: date) -> dict:
        """ビザ期限のステータス計算"""
        days = (expiration - date.today()).days
        return {
            "days_remaining": days,
            "is_expired": days < 0,
            "status": "expired" if days < 0 else "critical" if days <= 30 else "warning" if days <= 90 else "ok",
            "can_renew": 0 < days <= 90,
            "message": f"期限まで{days}日" if days > 0 else f"期限切れ（{abs(days)}日経過）"
        }

# ============================================================
# MODELOS
# ============================================================

class EmployeeBase(BaseModel):
    family_name: str = Field(..., min_length=1, max_length=100)
    given_name: str = Field(..., min_length=1, max_length=100)
    family_name_kanji: Optional[str] = None
    given_name_kanji: Optional[str] = None
    nationality: str
    date_of_birth: date
    sex: str = Field(..., pattern='^(male|female)$')
    marital_status: Optional[str] = None
    place_of_birth: Optional[str] = None
    home_town_city: Optional[str] = None
    
    # Contacto
    postal_code_japan: Optional[str] = None
    address_japan: Optional[str] = None
    telephone_japan: Optional[str] = None
    cellular_phone: Optional[str] = None
    email: Optional[str] = None
    
    # Pasaporte
    passport_number: str
    passport_expiration: date
    passport_issue_country: Optional[str] = None
    
    # Visa
    current_visa_status: Optional[str] = None
    current_period_of_stay: Optional[str] = None
    current_expiration_date: Optional[date] = None
    residence_card_number: Optional[str] = None
    
    # Educación
    school_location: Optional[str] = None
    school_name: Optional[str] = None
    graduation_date: Optional[date] = None
    major_field: Optional[str] = None
    has_it_qualification: bool = False
    it_qualification_name: Optional[str] = None
    japanese_level: Optional[str] = None
    
    # Criminal
    has_criminal_record: bool = False
    
    @validator('residence_card_number')
    def validate_card(cls, v):
        if v and not Validators.residence_card(v):
            raise ValueError('在留カード番号の形式が無効です（例：AB12345678CD）')
        return v.upper() if v else v
    
    @validator('postal_code_japan')
    def validate_postal(cls, v):
        if not Validators.postal_code(v):
            raise ValueError('郵便番号の形式が無効です')
        return v
    
    @validator('telephone_japan', 'cellular_phone')
    def validate_phone(cls, v):
        if not Validators.phone_japan(v):
            raise ValueError('電話番号の形式が無効です')
        return v

class EmployeeCreate(EmployeeBase):
    employee_code: Optional[str] = None

class HakenMoto(BaseModel):
    company_name: str
    corporation_number: Optional[str] = None
    employment_insurance_number: Optional[str] = None
    worker_dispatch_license: Optional[str] = None
    full_address: Optional[str] = None
    telephone: Optional[str] = None
    capital: Optional[int] = None
    annual_sales: Optional[int] = None
    total_employees: Optional[int] = None
    foreign_employees: Optional[int] = None
    representative_name: Optional[str] = None
    business_type_code: Optional[str] = None
    immigration_category: Optional[int] = Field(None, ge=1, le=4)
    
    @validator('corporation_number')
    def validate_corp(cls, v):
        if not Validators.corporation_number(v):
            raise ValueError('法人番号は13桁です')
        return v
    
    @validator('employment_insurance_number')
    def validate_ins(cls, v):
        if not Validators.insurance_number(v):
            raise ValueError('雇用保険番号は11桁です')
        return v

class HakenSaki(BaseModel):
    company_name: str
    branch_name: Optional[str] = None
    corporation_number: Optional[str] = None
    employment_insurance_number: Optional[str] = None
    full_address: Optional[str] = None
    telephone: Optional[str] = None
    capital: Optional[int] = None
    annual_sales: Optional[int] = None
    business_type_code: Optional[str] = None

class OCRData(BaseModel):
    zairyu_card: Optional[dict] = None
    passport: Optional[dict] = None

class VisaApplication(BaseModel):
    employee_id: int
    application_type: str = Field(..., pattern='^(認定|変更|更新)$')
    submission_office: str
    requested_period: str
    reason: str

# ============================================================
# ENDPOINTS - EMPLOYEES
# ============================================================

@app.post("/api/employees", tags=["Employees"])
async def create_employee(emp: EmployeeCreate):
    """従業員を作成"""
    if not emp.employee_code:
        pool = await get_db_pool()
    async with pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM employees")
            emp.employee_code = f"UNS-{date.today():%Y%m}-{count+1:04d}"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO employees (
                employee_code, family_name, given_name, family_name_kanji, given_name_kanji,
                nationality, date_of_birth, sex, marital_status, place_of_birth, home_town_city,
                postal_code_japan, address_japan, telephone_japan, cellular_phone, email,
                passport_number, passport_expiration, passport_issue_country,
                current_visa_status, current_period_of_stay, current_expiration_date, residence_card_number,
                school_location, school_name, graduation_date, major_field,
                has_it_qualification, it_qualification_name, japanese_level, has_criminal_record
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28,$29,$30,$31)
            RETURNING *
        """, emp.employee_code, emp.family_name, emp.given_name, emp.family_name_kanji, emp.given_name_kanji,
            emp.nationality, emp.date_of_birth, emp.sex, emp.marital_status, emp.place_of_birth, emp.home_town_city,
            emp.postal_code_japan, emp.address_japan, emp.telephone_japan, emp.cellular_phone, emp.email,
            emp.passport_number, emp.passport_expiration, emp.passport_issue_country,
            emp.current_visa_status, emp.current_period_of_stay, emp.current_expiration_date, emp.residence_card_number,
            emp.school_location, emp.school_name, emp.graduation_date, emp.major_field,
            emp.has_it_qualification, emp.it_qualification_name, emp.japanese_level, emp.has_criminal_record)
        
        result = dict(row)
        if result.get('current_expiration_date'):
            result['visa_status'] = Validators.visa_status(result['current_expiration_date'])
        return result

@app.get("/api/employees", tags=["Employees"])
async def list_employees(skip: int = 0, limit: int = 100, nationality: Optional[str] = None):
    """従業員一覧"""
    query = "SELECT * FROM employees WHERE employment_status = 'active'"
    params = []
    if nationality:
        query += " AND nationality = $1"
        params.append(nationality)
    query += f" ORDER BY current_expiration_date ASC LIMIT {limit} OFFSET {skip}"
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        results = []
        for row in rows:
            emp = dict(row)
            if emp.get('current_expiration_date'):
                emp['visa_status'] = Validators.visa_status(emp['current_expiration_date'])
            results.append(emp)
        return results

@app.get("/api/employees/{id}", tags=["Employees"])
async def get_employee(id: int):
    """従業員詳細"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM employees WHERE id = $1", id)
        if not row:
            raise HTTPException(404, "従業員が見つかりません")
        emp = dict(row)
        if emp.get('current_expiration_date'):
            emp['visa_status'] = Validators.visa_status(emp['current_expiration_date'])
        return emp

@app.put("/api/employees/{id}", tags=["Employees"])
async def update_employee(id: int, emp: EmployeeCreate):
    """従業員更新"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Check if exists
        exists = await conn.fetchval("SELECT 1 FROM employees WHERE id = $1", id)
        if not exists:
            raise HTTPException(404, "従業員が見つかりません")

        # Update
        row = await conn.fetchrow("""
            UPDATE employees SET
                family_name = $2, given_name = $3, family_name_kanji = $4, given_name_kanji = $5,
                nationality = $6, date_of_birth = $7, sex = $8, marital_status = $9, place_of_birth = $10, home_town_city = $11,
                postal_code_japan = $12, address_japan = $13, telephone_japan = $14, cellular_phone = $15, email = $16,
                passport_number = $17, passport_expiration = $18, passport_issue_country = $19,
                current_visa_status = $20, current_period_of_stay = $21, current_expiration_date = $22, residence_card_number = $23,
                school_location = $24, school_name = $25, graduation_date = $26, major_field = $27,
                has_it_qualification = $28, it_qualification_name = $29, japanese_level = $30, has_criminal_record = $31
            WHERE id = $1
            RETURNING *
        """, id, emp.family_name, emp.given_name, emp.family_name_kanji, emp.given_name_kanji,
            emp.nationality, emp.date_of_birth, emp.sex, emp.marital_status, emp.place_of_birth, emp.home_town_city,
            emp.postal_code_japan, emp.address_japan, emp.telephone_japan, emp.cellular_phone, emp.email,
            emp.passport_number, emp.passport_expiration, emp.passport_issue_country,
            emp.current_visa_status, emp.current_period_of_stay, emp.current_expiration_date, emp.residence_card_number,
            emp.school_location, emp.school_name, emp.graduation_date, emp.major_field,
            emp.has_it_qualification, emp.it_qualification_name, emp.japanese_level, emp.has_criminal_record)
        
        return dict(row)

@app.delete("/api/employees/{id}", tags=["Employees"])
async def delete_employee(id: int):
    """従業員削除 (論理削除)"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("UPDATE employees SET employment_status = 'inactive' WHERE id = $1", id)
        if result == "DELETE 0": # UPDATE 0 in this case but checking row count
             # asyncpg execute returns "UPDATE N"
             if result == "UPDATE 0":
                raise HTTPException(404, "従業員が見つかりません")
        return {"message": "削除しました"}

@app.put("/api/employees/{id}", tags=["Employees"])
async def update_employee(id: int, emp: EmployeeCreate):
    """従業員更新"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Check if exists
        exists = await conn.fetchval("SELECT 1 FROM employees WHERE id = $1", id)
        if not exists:
            raise HTTPException(404, "従業員が見つかりません")

        # Update
        row = await conn.fetchrow("""
            UPDATE employees SET
                family_name = $2, given_name = $3, family_name_kanji = $4, given_name_kanji = $5,
                nationality = $6, date_of_birth = $7, sex = $8, marital_status = $9, place_of_birth = $10, home_town_city = $11,
                postal_code_japan = $12, address_japan = $13, telephone_japan = $14, cellular_phone = $15, email = $16,
                passport_number = $17, passport_expiration = $18, passport_issue_country = $19,
                current_visa_status = $20, current_period_of_stay = $21, current_expiration_date = $22, residence_card_number = $23,
                school_location = $24, school_name = $25, graduation_date = $26, major_field = $27,
                has_it_qualification = $28, it_qualification_name = $29, japanese_level = $30, has_criminal_record = $31
            WHERE id = $1
            RETURNING *
        """, id, emp.family_name, emp.given_name, emp.family_name_kanji, emp.given_name_kanji,
            emp.nationality, emp.date_of_birth, emp.sex, emp.marital_status, emp.place_of_birth, emp.home_town_city,
            emp.postal_code_japan, emp.address_japan, emp.telephone_japan, emp.cellular_phone, emp.email,
            emp.passport_number, emp.passport_expiration, emp.passport_issue_country,
            emp.current_visa_status, emp.current_period_of_stay, emp.current_expiration_date, emp.residence_card_number,
            emp.school_location, emp.school_name, emp.graduation_date, emp.major_field,
            emp.has_it_qualification, emp.it_qualification_name, emp.japanese_level, emp.has_criminal_record)
        
        return dict(row)

@app.delete("/api/employees/{id}", tags=["Employees"])
async def delete_employee(id: int):
    """従業員削除 (論理削除)"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("UPDATE employees SET employment_status = 'inactive' WHERE id = $1", id)
        if result == "DELETE 0": # UPDATE 0 in this case but checking row count
             # asyncpg execute returns "UPDATE N"
             if result == "UPDATE 0":
                raise HTTPException(404, "従業員が見つかりません")
        return {"message": "削除しました"}

@app.get("/api/employees/card/{card_number}", tags=["Employees"])
async def get_by_card(card_number: str):
    """在留カード番号で検索"""
    if not Validators.residence_card(card_number):
        raise HTTPException(400, "在留カード番号の形式が無効です")
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM employees WHERE residence_card_number = $1",
            card_number.upper()
        )
        if not row:
            raise HTTPException(404, "従業員が見つかりません")
        return dict(row)

# ============================================================
# ENDPOINTS - OCR
# ============================================================

@app.post("/api/ocr/import", tags=["OCR"])
async def import_ocr(data: OCRData):
    """OCRデータをインポート"""
    result = {}
    
    if data.zairyu_card:
        zc = data.zairyu_card
        if zc.get('name'):
            parts = zc['name'].split(' ', 1)
            result['family_name'] = parts[0]
            result['given_name'] = parts[1] if len(parts) > 1 else ''
        result['family_name_kanji'] = zc.get('nameKanji')
        result['nationality'] = zc.get('nationality')
        result['date_of_birth'] = zc.get('dateOfBirth')
        result['sex'] = zc.get('sex')
        result['current_visa_status'] = zc.get('statusOfResidence')
        result['current_period_of_stay'] = zc.get('periodOfStay')
        result['current_expiration_date'] = zc.get('expirationDate')
        result['residence_card_number'] = zc.get('cardNumber')
        result['address_japan'] = zc.get('address')
    
    if data.passport:
        pp = data.passport
        if not result.get('family_name'):
            result['family_name'] = pp.get('surname')
        if not result.get('given_name'):
            result['given_name'] = pp.get('givenNames')
        result['passport_number'] = pp.get('passportNumber')
        result['passport_expiration'] = pp.get('dateOfExpiry')
        result['passport_issue_country'] = pp.get('issuingCountry')
        result['place_of_birth'] = pp.get('placeOfBirth')
        result['home_town_city'] = pp.get('placeOfBirth')
    
    # Limpiar None
    result = {k: v for k, v in result.items() if v}
    
    # Verificar si existe
    existing = None
    if result.get('residence_card_number'):
        pool = await get_db_pool()
    async with pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT id FROM employees WHERE residence_card_number = $1",
                result['residence_card_number'].upper()
            )
    
    return {
        "extracted": result,
        "is_existing": existing is not None,
        "existing_id": existing['id'] if existing else None
    }

# ============================================================
# ENDPOINTS - ALERTS
# ============================================================

@app.get("/api/alerts/expiring", tags=["Alerts"])
async def expiring_visas(days: int = 90):
    """期限切れ間近のビザ"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, employee_code, family_name, given_name, nationality,
                   current_visa_status, current_expiration_date, residence_card_number,
                   (current_expiration_date - CURRENT_DATE) as days_left
            FROM employees
            WHERE employment_status = 'active'
              AND current_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + $1::interval
            ORDER BY current_expiration_date
        """, f"{days} days")
        
        alerts = []
        for row in rows:
            a = dict(row)
            d = a['days_left'].days
            a['days_remaining'] = d
            a['urgency'] = 'critical' if d <= 30 else 'warning' if d <= 60 else 'info'
            del a['days_left']
            alerts.append(a)
        
        return {
            "total": len(alerts),
            "critical": len([a for a in alerts if a['urgency'] == 'critical']),
            "alerts": alerts
        }

# ============================================================
# ENDPOINTS - VALIDATE
# ============================================================

@app.post("/api/validate/card", tags=["Validation"])
async def validate_card(card_number: str):
    """在留カード番号を検証"""
    valid = Validators.residence_card(card_number)
    return {
        "input": card_number,
        "valid": valid,
        "formatted": card_number.upper() if valid else None,
        "message": "有効" if valid else "無効（例：AB12345678CD）"
    }

@app.post("/api/validate/corporation", tags=["Validation"])
async def validate_corp(number: str):
    """法人番号を検証"""
    valid = Validators.corporation_number(number)
    return {"input": number, "valid": valid, "message": "有効" if valid else "13桁の数字が必要"}

# ============================================================
# ENDPOINTS - STATS
# ============================================================

@app.get("/api/stats", tags=["Stats"])
async def dashboard_stats():
    """ダッシュボード統計"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM employees WHERE employment_status='active'")
        
        by_nat = await conn.fetch("""
            SELECT nationality, COUNT(*) as count FROM employees 
            WHERE employment_status='active' GROUP BY nationality ORDER BY count DESC
        """)
        
        exp30 = await conn.fetchval("""
            SELECT COUNT(*) FROM employees WHERE employment_status='active'
            AND current_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + '30 days'
        """)
        
        exp90 = await conn.fetchval("""
            SELECT COUNT(*) FROM employees WHERE employment_status='active'
            AND current_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + '90 days'
        """)
        
        return {
            "total_employees": total,
            "by_nationality": [dict(r) for r in by_nat],
            "expiring_30_days": exp30,
            "expiring_90_days": exp90
        }

# ============================================================
# ENDPOINTS - OCR
# ============================================================

@app.post("/api/ocr/scan", tags=["OCR"])
async def ocr_scan(file: bytes = None):
    """
    OCRで在留カード・パスポートを読み取り
    Scan residence card or passport using OCR

    Note: This is a placeholder. Real OCR requires Claude Vision API or similar.
    """
    # Placeholder response - simulates OCR result
    return {
        "success": True,
        "document_type": "residence_card",
        "data": {
            "residence_card_number": "",
            "name": "",
            "name_romaji": "",
            "nationality": "",
            "visa_status": "技術・人文知識・国際業務",
            "expiration_date": "",
            "date_of_birth": ""
        },
        "confidence": 0.0,
        "message": "OCR機能は開発中です。手動で入力してください。"
    }

# ============================================================
# ENDPOINTS - EXCEL GENERATION
# ============================================================

from fastapi.responses import StreamingResponse
from excel_generator import VisaFormExcelGenerator, generate_visa_renewal_excel

@app.post("/api/excel/generate", tags=["Excel"])
async def generate_excel(data: dict):
    """
    在留期間更新許可申請書を生成
    Generate visa renewal application form (Excel)
    """
    try:
        excel_file = generate_visa_renewal_excel(data)

        # Get employee name for filename
        name = f"{data.get('family_name', '')}_{data.get('given_name', '')}"
        filename = f"在留期間更新許可申請書_{name}.xlsx"

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel生成エラー: {str(e)}")

@app.post("/api/visa/coe/generate", tags=["Excel"])
async def generate_coe_excel(data: dict):
    """
    在留資格認定証明書交付申請書を生成
    Generate Certificate of Eligibility application form (Excel)
    """
    try:
        # Use the same generator but mark as COE type
        generator = VisaFormExcelGenerator()

        # Add COE-specific fields
        data['form_type'] = 'coe'
        data['submission_office'] = data.get('submission_office', '名古屋')

        # Generate renewal form (COE format is similar)
        excel_file = generator.generate_renewal_form(data)

        # Get applicant name for filename
        name = f"{data.get('family_name', '')}_{data.get('given_name', '')}"
        filename = f"在留資格認定証明書交付申請書_{name}.xlsx"

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel生成エラー: {str(e)}")

@app.get("/health")
async def health():
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "error", "db": "disconnected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
