# ============================================================
# UNS VISA SYSTEM - Haken Saki (派遣先) Module
# CRUD operations for client companies
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
import re
from database import get_db_pool

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
    pool = await get_db_pool()
    
    # Create full address if not provided
    data = company.dict()
    if not data.get('full_address'):
        parts = [data.get('prefecture', ''), data.get('city', ''), 
                 data.get('address_line1', ''), data.get('address_line2', '')]
        data['full_address'] = ''.join(filter(None, parts))
    
    async with pool.acquire() as conn:
        # Check for duplicates
        existing = await conn.fetchrow(
            "SELECT id FROM haken_saki_company WHERE company_name = $1 AND branch_name IS NOT DISTINCT FROM $2",
            company.company_name, company.branch_name
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"この派遣先は既に登録されています: {company.company_name}"
            )

        # Insert
        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i+1}" for i in range(len(values))]
        
        query = f"""
            INSERT INTO haken_saki_company ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        
        row = await conn.fetchrow(query, *values)
        return dict(row)

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
    pool = await get_db_pool()
    
    query = "SELECT * FROM haken_saki_company WHERE 1=1"
    params = []
    
    if active_only:
        query += " AND is_active = TRUE"
    
    if search:
        search_lower = f"%{search.lower()}%"
        query += """ AND (
            LOWER(company_name) LIKE $1 OR 
            LOWER(branch_name) LIKE $1 OR 
            LOWER(full_address) LIKE $1
        )"""
        params.append(search_lower)
    
    query += f" ORDER BY id DESC LIMIT {limit} OFFSET {skip}"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]

@router.get("/{company_id}", response_model=HakenSakiResponse)
async def get_haken_saki(company_id: int):
    """
    派遣先会社を取得
    Get a client company by ID
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM haken_saki_company WHERE id = $1", company_id)
        if not row:
            raise HTTPException(status_code=404, detail="派遣先が見つかりません")
        return dict(row)

@router.put("/{company_id}", response_model=HakenSakiResponse)
async def update_haken_saki(company_id: int, update_data: HakenSakiUpdate):
    """
    派遣先会社を更新
    Update a client company
    """
    pool = await get_db_pool()
    
    data = update_data.dict(exclude_unset=True)
    if not data:
        return await get_haken_saki(company_id)
        
    set_clauses = []
    values = []
    for i, (k, v) in enumerate(data.items()):
        set_clauses.append(f"{k} = ${i+2}")
        values.append(v)
    
    query = f"""
        UPDATE haken_saki_company 
        SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = $1
        RETURNING *
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, company_id, *values)
        if not row:
            raise HTTPException(status_code=404, detail="派遣先が見つかりません")
        return dict(row)

@router.delete("/{company_id}")
async def delete_haken_saki(company_id: int, hard_delete: bool = False):
    """
    派遣先会社を削除（論理削除）
    Delete a client company (soft delete by default)
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        if hard_delete:
            result = await conn.execute("DELETE FROM haken_saki_company WHERE id = $1", company_id)
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail="派遣先が見つかりません")
            return {"message": "派遣先を完全に削除しました"}
        else:
            row = await conn.fetchrow("""
                UPDATE haken_saki_company 
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
                RETURNING id
            """, company_id)
            if not row:
                raise HTTPException(status_code=404, detail="派遣先が見つかりません")
            return {"message": "派遣先を無効化しました"}

@router.post("/bulk-import")
async def bulk_import_haken_saki(import_data: HakenSakiBulkImport):
    """
    派遣先会社を一括インポート
    Bulk import client companies
    """
    pool = await get_db_pool()
    
    results = {
        "success": 0,
        "failed": 0,
        "errors": [],
        "imported": []
    }
    
    async with pool.acquire() as conn:
        for company in import_data.companies:
            try:
                # Check duplicate
                existing = await conn.fetchrow(
                    "SELECT id FROM haken_saki_company WHERE company_name = $1 AND branch_name IS NOT DISTINCT FROM $2",
                    company.company_name, company.branch_name
                )
                
                if existing:
                    results['failed'] += 1
                    results['errors'].append({
                        "company": company.company_name,
                        "error": "既に登録されています"
                    })
                    continue
                
                # Prepare data
                data = company.dict()
                if not data.get('full_address'):
                    parts = [data.get('prefecture', ''), data.get('city', ''), 
                             data.get('address_line1', ''), data.get('address_line2', '')]
                    data['full_address'] = ''.join(filter(None, parts))
                
                columns = list(data.keys())
                values = list(data.values())
                placeholders = [f"${i+1}" for i in range(len(values))]
                
                query = f"""
                    INSERT INTO haken_saki_company ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                    RETURNING id, company_name, branch_name
                """
                
                row = await conn.fetchrow(query, *values)
                
                results['success'] += 1
                results['imported'].append(dict(row))
                
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
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM haken_saki_company WHERE is_active = TRUE")
        
        # Simple stats for now
        return {
            "total_companies": total,
            "total_employees_at_clients": 0, # To be implemented with dispatch assignments
            "total_foreign_at_clients": 0,
            "by_prefecture": {},
            "by_business_type": {}
        }

@router.get("/search/by-name")
async def search_haken_saki_by_name(name: str, limit: int = 10):
    """
    会社名で派遣先を検索
    Search client companies by name (for autocomplete)
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, company_name, branch_name, full_address 
            FROM haken_saki_company 
            WHERE is_active = TRUE 
            AND LOWER(company_name) LIKE $1
            LIMIT $2
        """, f"%{name.lower()}%", limit)
        
        return [dict(row) for row in rows]
