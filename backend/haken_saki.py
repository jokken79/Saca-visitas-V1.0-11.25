# ============================================================
# UNS VISA SYSTEM - Haken Saki (派遣先) Module
# CRUD operations for client companies
# PostgreSQL Version
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
import re

# Import database pool from main
from main import db_pool

router = APIRouter(prefix="/api/haken-saki", tags=["Haken Saki (派遣先)"])

# ============================================================
# MODELS
# ============================================================

class HakenSakiBase(BaseModel):
    """Modelo base para派遣先"""

    # Información básica
    company_name: str = Field(..., min_length=1, max_length=200)
    company_name_kana: Optional[str] = Field(None, max_length=200)
    branch_name: Optional[str] = Field(None, max_length=100)

    # Números de registro
    corporation_number: Optional[str] = Field(None, max_length=13)
    employment_insurance_number: Optional[str] = Field(None, max_length=11)

    # Dirección
    postal_code: Optional[str] = Field(None, max_length=8)
    prefecture: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    full_address: Optional[str] = None

    # Contacto
    telephone: Optional[str] = Field(None, max_length=20)
    fax: Optional[str] = Field(None, max_length=20)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[str] = Field(None, max_length=100)

    # Información financiera
    capital: Optional[int] = None
    annual_sales: Optional[int] = None

    # Empleados
    total_employees: Optional[int] = None
    foreign_employees: Optional[int] = None
    trainee_count: Optional[int] = 0

    # Negocio
    business_type_code: Optional[str] = Field(None, max_length=10)
    business_type_name: Optional[str] = Field(None, max_length=100)
    industry_sector: Optional[str] = Field(None, max_length=100)

    # Contrato
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_status: Optional[str] = "active"

    # Notas
    notes: Optional[str] = None

    @validator('corporation_number')
    def validate_corp_number(cls, v):
        if v:
            clean = v.replace('-', '').replace(' ', '')
            if not re.match(r'^\d{13}$', clean):
                raise ValueError('法人番号は13桁の数字である必要があります')
            return clean
        return v

    @validator('employment_insurance_number')
    def validate_insurance_number(cls, v):
        if v:
            clean = v.replace('-', '').replace(' ', '')
            if not re.match(r'^\d{11}$', clean):
                raise ValueError('雇用保険番号は11桁の数字である必要があります')
            return clean
        return v

    @validator('telephone', 'fax')
    def validate_phone(cls, v):
        if v:
            clean = v.replace('-', '').replace(' ', '')
            if not re.match(r'^0\d{9,10}$', clean):
                raise ValueError('電話番号の形式が無効です')
        return v

    @validator('postal_code')
    def validate_postal(cls, v):
        if v:
            clean = v.replace('-', '').replace(' ', '')
            if not re.match(r'^\d{7}$', clean):
                raise ValueError('郵便番号は7桁の数字である必要があります')
            return f"{clean[:3]}-{clean[3:]}"
        return v

class HakenSakiCreate(HakenSakiBase):
    """Modelo para crear派遣先"""
    pass

class HakenSakiUpdate(BaseModel):
    """Modelo para actualizar派遣先 (todos opcionales)"""
    company_name: Optional[str] = None
    company_name_kana: Optional[str] = None
    branch_name: Optional[str] = None
    corporation_number: Optional[str] = None
    employment_insurance_number: Optional[str] = None
    postal_code: Optional[str] = None
    prefecture: Optional[str] = None
    city: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    full_address: Optional[str] = None
    telephone: Optional[str] = None
    fax: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    capital: Optional[int] = None
    annual_sales: Optional[int] = None
    total_employees: Optional[int] = None
    foreign_employees: Optional[int] = None
    trainee_count: Optional[int] = None
    business_type_code: Optional[str] = None
    business_type_name: Optional[str] = None
    industry_sector: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_status: Optional[str] = None
    notes: Optional[str] = None

class HakenSakiResponse(HakenSakiBase):
    """Modelo de respuesta"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    employee_count: Optional[int] = None  # Número de empleados asignados

    class Config:
        from_attributes = True

class HakenSakiBulkImport(BaseModel):
    """Modelo para importación masiva"""
    companies: List[HakenSakiCreate]

# ============================================================
# ENDPOINTS
# ============================================================

@router.post("", response_model=HakenSakiResponse)
async def create_haken_saki(company: HakenSakiCreate):
    """
    派遣先会社を登録
    Create a new client company (派遣先)
    """
    # Check for duplicates
    async with db_pool.acquire() as conn:
        if company.branch_name:
            existing = await conn.fetchrow(
                """SELECT id FROM haken_saki_company
                   WHERE company_name = $1 AND branch_name = $2""",
                company.company_name, company.branch_name
            )
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"この派遣先は既に登録されています: {company.company_name} - {company.branch_name}"
                )
        else:
            existing = await conn.fetchrow(
                """SELECT id FROM haken_saki_company
                   WHERE company_name = $1 AND branch_name IS NULL""",
                company.company_name
            )
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"この派遣先は既に登録されています: {company.company_name}"
                )

        # Create full address if not provided
        data = company.dict()
        if not data.get('full_address'):
            parts = [
                data.get('prefecture', ''),
                data.get('city', ''),
                data.get('address_line1', ''),
                data.get('address_line2', '')
            ]
            data['full_address'] = ''.join(filter(None, parts))

        # Insert into database
        row = await conn.fetchrow("""
            INSERT INTO haken_saki_company (
                company_name, company_name_kana, branch_name,
                corporation_number, employment_insurance_number,
                postal_code, prefecture, city, address_line1, address_line2, full_address,
                telephone, fax, contact_person, contact_email,
                capital, annual_sales,
                total_employees, foreign_employees, trainee_count,
                business_type_code, business_type_name, industry_sector,
                contract_start_date, contract_end_date, contract_status,
                notes, is_active
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28)
            RETURNING *
        """,
            data['company_name'], data.get('company_name_kana'), data.get('branch_name'),
            data.get('corporation_number'), data.get('employment_insurance_number'),
            data.get('postal_code'), data.get('prefecture'), data.get('city'),
            data.get('address_line1'), data.get('address_line2'), data.get('full_address'),
            data.get('telephone'), data.get('fax'), data.get('contact_person'), data.get('contact_email'),
            data.get('capital'), data.get('annual_sales'),
            data.get('total_employees'), data.get('foreign_employees'), data.get('trainee_count'),
            data.get('business_type_code'), data.get('business_type_name'), data.get('industry_sector'),
            data.get('contract_start_date'), data.get('contract_end_date'), data.get('contract_status', 'active'),
            data.get('notes'), True
        )

        # Get employee count
        employee_count = await conn.fetchval("""
            SELECT COUNT(*) FROM dispatch_assignments
            WHERE haken_saki_id = $1 AND assignment_status = 'active'
        """, row['id'])

        result = dict(row)
        result['employee_count'] = employee_count
        return result

@router.get("", response_model=List[HakenSakiResponse])
async def list_haken_saki(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    active_only: bool = True
):
    """
    派遣先会社一覧を取得
    List all client companies
    """
    async with db_pool.acquire() as conn:
        query = "SELECT * FROM haken_saki_company WHERE 1=1"
        params = []
        param_count = 0

        if active_only:
            query += " AND is_active = TRUE"

        if search:
            param_count += 1
            query += f""" AND (
                LOWER(company_name) LIKE $${param_count} OR
                LOWER(branch_name) LIKE $${param_count} OR
                LOWER(full_address) LIKE $${param_count}
            )"""
            params.append(f"%{search.lower()}%")

        query += f" ORDER BY company_name, branch_name LIMIT {limit} OFFSET {skip}"

        rows = await conn.fetch(query, *params)

        results = []
        for row in rows:
            company = dict(row)
            # Get employee count
            employee_count = await conn.fetchval("""
                SELECT COUNT(*) FROM dispatch_assignments
                WHERE haken_saki_id = $1 AND assignment_status = 'active'
            """, company['id'])
            company['employee_count'] = employee_count
            results.append(company)

        return results

@router.get("/{company_id}", response_model=HakenSakiResponse)
async def get_haken_saki(company_id: int):
    """
    派遣先会社を取得
    Get a client company by ID
    """
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM haken_saki_company WHERE id = $1",
            company_id
        )

        if not row:
            raise HTTPException(status_code=404, detail="派遣先が見つかりません")

        company = dict(row)

        # Get employee count
        employee_count = await conn.fetchval("""
            SELECT COUNT(*) FROM dispatch_assignments
            WHERE haken_saki_id = $1 AND assignment_status = 'active'
        """, company_id)
        company['employee_count'] = employee_count

        return company

@router.put("/{company_id}", response_model=HakenSakiResponse)
async def update_haken_saki(company_id: int, update_data: HakenSakiUpdate):
    """
    派遣先会社を更新
    Update a client company
    """
    async with db_pool.acquire() as conn:
        # Check if exists
        existing = await conn.fetchrow(
            "SELECT id FROM haken_saki_company WHERE id = $1",
            company_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="派遣先が見つかりません")

        # Build update query dynamically
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            # No changes, just return current data
            return await get_haken_saki(company_id)

        # Build SET clause
        set_clauses = []
        params = []
        param_count = 0

        for key, value in update_dict.items():
            param_count += 1
            set_clauses.append(f"{key} = ${param_count}")
            params.append(value)

        param_count += 1
        params.append(company_id)

        query = f"""
            UPDATE haken_saki_company
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
            RETURNING *
        """

        row = await conn.fetchrow(query, *params)

        company = dict(row)

        # Get employee count
        employee_count = await conn.fetchval("""
            SELECT COUNT(*) FROM dispatch_assignments
            WHERE haken_saki_id = $1 AND assignment_status = 'active'
        """, company_id)
        company['employee_count'] = employee_count

        return company

@router.delete("/{company_id}")
async def delete_haken_saki(company_id: int, hard_delete: bool = False):
    """
    派遣先会社を削除（論理削除）
    Delete a client company (soft delete by default)
    """
    async with db_pool.acquire() as conn:
        # Check if exists
        existing = await conn.fetchrow(
            "SELECT id FROM haken_saki_company WHERE id = $1",
            company_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="派遣先が見つかりません")

        if hard_delete:
            await conn.execute(
                "DELETE FROM haken_saki_company WHERE id = $1",
                company_id
            )
            return {"message": "派遣先を完全に削除しました"}
        else:
            await conn.execute(
                "UPDATE haken_saki_company SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE id = $1",
                company_id
            )
            return {"message": "派遣先を無効化しました"}

@router.post("/bulk-import")
async def bulk_import_haken_saki(import_data: HakenSakiBulkImport):
    """
    派遣先会社を一括インポート
    Bulk import client companies
    """
    results = {
        "success": 0,
        "failed": 0,
        "errors": [],
        "imported": []
    }

    async with db_pool.acquire() as conn:
        for company in import_data.companies:
            try:
                # Check for duplicates
                if company.branch_name:
                    existing = await conn.fetchrow(
                        """SELECT id FROM haken_saki_company
                           WHERE company_name = $1 AND branch_name = $2""",
                        company.company_name, company.branch_name
                    )
                else:
                    existing = await conn.fetchrow(
                        """SELECT id FROM haken_saki_company
                           WHERE company_name = $1 AND branch_name IS NULL""",
                        company.company_name
                    )

                if existing:
                    results['failed'] += 1
                    results['errors'].append({
                        "company": company.company_name,
                        "error": "既に登録されています"
                    })
                    continue

                # Create full address if not provided
                data = company.dict()
                if not data.get('full_address'):
                    parts = [
                        data.get('prefecture', ''),
                        data.get('city', ''),
                        data.get('address_line1', ''),
                        data.get('address_line2', '')
                    ]
                    data['full_address'] = ''.join(filter(None, parts))

                # Insert
                row = await conn.fetchrow("""
                    INSERT INTO haken_saki_company (
                        company_name, company_name_kana, branch_name,
                        corporation_number, employment_insurance_number,
                        postal_code, prefecture, city, address_line1, address_line2, full_address,
                        telephone, fax, contact_person, contact_email,
                        capital, annual_sales,
                        total_employees, foreign_employees, trainee_count,
                        business_type_code, business_type_name, industry_sector,
                        contract_start_date, contract_end_date, contract_status,
                        notes, is_active
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24,$25,$26,$27,$28)
                    RETURNING id, company_name, branch_name
                """,
                    data['company_name'], data.get('company_name_kana'), data.get('branch_name'),
                    data.get('corporation_number'), data.get('employment_insurance_number'),
                    data.get('postal_code'), data.get('prefecture'), data.get('city'),
                    data.get('address_line1'), data.get('address_line2'), data.get('full_address'),
                    data.get('telephone'), data.get('fax'), data.get('contact_person'), data.get('contact_email'),
                    data.get('capital'), data.get('annual_sales'),
                    data.get('total_employees'), data.get('foreign_employees'), data.get('trainee_count'),
                    data.get('business_type_code'), data.get('business_type_name'), data.get('industry_sector'),
                    data.get('contract_start_date'), data.get('contract_end_date'), data.get('contract_status', 'active'),
                    data.get('notes'), True
                )

                results['success'] += 1
                results['imported'].append({
                    "id": row['id'],
                    "company_name": row['company_name'],
                    "branch_name": row['branch_name']
                })

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    "company": company.company_name,
                    "error": str(e)
                })

    return results

@router.get("/stats/summary")
async def get_haken_saki_stats():
    """
    派遣先統計情報を取得
    Get statistics about client companies
    """
    async with db_pool.acquire() as conn:
        # Total active companies
        total_companies = await conn.fetchval(
            "SELECT COUNT(*) FROM haken_saki_company WHERE is_active = TRUE"
        )

        # Total employees at all clients
        total_employees = await conn.fetchval("""
            SELECT COALESCE(SUM(total_employees), 0)
            FROM haken_saki_company WHERE is_active = TRUE
        """)

        # Total foreign employees at all clients
        total_foreign = await conn.fetchval("""
            SELECT COALESCE(SUM(foreign_employees), 0)
            FROM haken_saki_company WHERE is_active = TRUE
        """)

        # Group by prefecture
        by_prefecture_rows = await conn.fetch("""
            SELECT prefecture, COUNT(*) as count
            FROM haken_saki_company
            WHERE is_active = TRUE
            GROUP BY prefecture
            ORDER BY count DESC
        """)
        by_prefecture = {row['prefecture'] or '不明': row['count'] for row in by_prefecture_rows}

        # Group by business type
        by_business_rows = await conn.fetch("""
            SELECT business_type_name, COUNT(*) as count
            FROM haken_saki_company
            WHERE is_active = TRUE
            GROUP BY business_type_name
            ORDER BY count DESC
        """)
        by_business = {row['business_type_name'] or '不明': row['count'] for row in by_business_rows}

        return {
            "total_companies": total_companies,
            "total_employees_at_clients": total_employees,
            "total_foreign_at_clients": total_foreign,
            "by_prefecture": by_prefecture,
            "by_business_type": by_business
        }

@router.get("/search/by-name")
async def search_haken_saki_by_name(name: str, limit: int = 10):
    """
    会社名で派遣先を検索
    Search client companies by name (for autocomplete)
    """
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, company_name, branch_name, full_address
            FROM haken_saki_company
            WHERE is_active = TRUE
              AND LOWER(company_name) LIKE $1
            ORDER BY company_name, branch_name
            LIMIT $2
        """, f"%{name.lower()}%", limit)

        results = [dict(row) for row in rows]
        return results
