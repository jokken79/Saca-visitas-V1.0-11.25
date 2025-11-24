# ============================================================
# UNS VISA SYSTEM - Haken Saki (派遣先) Module
# CRUD operations for client companies
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
import re

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

# Simulated database (replace with actual DB operations)
haken_saki_db = []
next_id = 1

@router.post("", response_model=HakenSakiResponse)
async def create_haken_saki(company: HakenSakiCreate):
    """
    派遣先会社を登録
    Create a new client company (派遣先)
    """
    global next_id
    
    # Check for duplicates
    for existing in haken_saki_db:
        if existing['company_name'] == company.company_name:
            if company.branch_name:
                if existing.get('branch_name') == company.branch_name:
                    raise HTTPException(
                        status_code=400,
                        detail=f"この派遣先は既に登録されています: {company.company_name} - {company.branch_name}"
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"この派遣先は既に登録されています: {company.company_name}"
                )
    
    # Create full address if not provided
    data = company.dict()
    if not data.get('full_address'):
        parts = [data.get('prefecture', ''), data.get('city', ''), 
                 data.get('address_line1', ''), data.get('address_line2', '')]
        data['full_address'] = ''.join(filter(None, parts))
    
    # Add metadata
    data['id'] = next_id
    data['created_at'] = datetime.now()
    data['updated_at'] = datetime.now()
    data['is_active'] = True
    data['employee_count'] = 0
    
    haken_saki_db.append(data)
    next_id += 1
    
    return data

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
    results = haken_saki_db
    
    if active_only:
        results = [r for r in results if r.get('is_active', True)]
    
    if search:
        search_lower = search.lower()
        results = [r for r in results if 
                   search_lower in r.get('company_name', '').lower() or
                   search_lower in r.get('branch_name', '').lower() or
                   search_lower in r.get('full_address', '').lower()]
    
    return results[skip:skip + limit]

@router.get("/{company_id}", response_model=HakenSakiResponse)
async def get_haken_saki(company_id: int):
    """
    派遣先会社を取得
    Get a client company by ID
    """
    for company in haken_saki_db:
        if company['id'] == company_id:
            return company
    
    raise HTTPException(status_code=404, detail="派遣先が見つかりません")

@router.put("/{company_id}", response_model=HakenSakiResponse)
async def update_haken_saki(company_id: int, update_data: HakenSakiUpdate):
    """
    派遣先会社を更新
    Update a client company
    """
    for i, company in enumerate(haken_saki_db):
        if company['id'] == company_id:
            update_dict = update_data.dict(exclude_unset=True)
            haken_saki_db[i].update(update_dict)
            haken_saki_db[i]['updated_at'] = datetime.now()
            return haken_saki_db[i]
    
    raise HTTPException(status_code=404, detail="派遣先が見つかりません")

@router.delete("/{company_id}")
async def delete_haken_saki(company_id: int, hard_delete: bool = False):
    """
    派遣先会社を削除（論理削除）
    Delete a client company (soft delete by default)
    """
    for i, company in enumerate(haken_saki_db):
        if company['id'] == company_id:
            if hard_delete:
                del haken_saki_db[i]
                return {"message": "派遣先を完全に削除しました"}
            else:
                haken_saki_db[i]['is_active'] = False
                haken_saki_db[i]['updated_at'] = datetime.now()
                return {"message": "派遣先を無効化しました"}
    
    raise HTTPException(status_code=404, detail="派遣先が見つかりません")

@router.post("/bulk-import")
async def bulk_import_haken_saki(import_data: HakenSakiBulkImport):
    """
    派遣先会社を一括インポート
    Bulk import client companies
    """
    global next_id
    
    results = {
        "success": 0,
        "failed": 0,
        "errors": [],
        "imported": []
    }
    
    for company in import_data.companies:
        try:
            # Check for duplicates
            duplicate = False
            for existing in haken_saki_db:
                if existing['company_name'] == company.company_name:
                    if company.branch_name and existing.get('branch_name') == company.branch_name:
                        duplicate = True
                        break
                    elif not company.branch_name:
                        duplicate = True
                        break
            
            if duplicate:
                results['failed'] += 1
                results['errors'].append({
                    "company": company.company_name,
                    "error": "既に登録されています"
                })
                continue
            
            # Create
            data = company.dict()
            if not data.get('full_address'):
                parts = [data.get('prefecture', ''), data.get('city', ''), 
                         data.get('address_line1', ''), data.get('address_line2', '')]
                data['full_address'] = ''.join(filter(None, parts))
            
            data['id'] = next_id
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            data['is_active'] = True
            data['employee_count'] = 0
            
            haken_saki_db.append(data)
            next_id += 1
            
            results['success'] += 1
            results['imported'].append({
                "id": data['id'],
                "company_name": data['company_name'],
                "branch_name": data.get('branch_name')
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
    active = [c for c in haken_saki_db if c.get('is_active', True)]
    
    total_employees = sum(c.get('total_employees', 0) for c in active)
    total_foreign = sum(c.get('foreign_employees', 0) for c in active)
    
    # Group by prefecture
    by_prefecture = {}
    for c in active:
        pref = c.get('prefecture', '不明')
        by_prefecture[pref] = by_prefecture.get(pref, 0) + 1
    
    # Group by business type
    by_business = {}
    for c in active:
        biz = c.get('business_type_name', '不明')
        by_business[biz] = by_business.get(biz, 0) + 1
    
    return {
        "total_companies": len(active),
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
    results = []
    name_lower = name.lower()
    
    for company in haken_saki_db:
        if not company.get('is_active', True):
            continue
        
        if name_lower in company.get('company_name', '').lower():
            results.append({
                "id": company['id'],
                "company_name": company['company_name'],
                "branch_name": company.get('branch_name'),
                "full_address": company.get('full_address')
            })
            
            if len(results) >= limit:
                break
    
    return results
