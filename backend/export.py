# ============================================================
# UNS VISA SYSTEM - Export Module
# Export endpoints for Excel forms
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from database import get_db_pool
from excel_generator import generate_visa_renewal_excel, VisaFormExcelGenerator
from datetime import date
import io
import asyncpg

router = APIRouter(prefix="/api/export", tags=["Export"])

@router.get("/visa-renewal/{employee_id}")
async def export_visa_renewal(employee_id: int):
    """
    在留期間更新許可申請書をエクスポート
    Export Visa Renewal Application Form (Excel)
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # 1. Get Employee Data
        emp_row = await conn.fetchrow("SELECT * FROM employees WHERE id = $1", employee_id)
        if not emp_row:
            raise HTTPException(404, "従業員が見つかりません")
        
        employee = dict(emp_row)

        # 2. Get Company Data (UNS)
        try:
            company_row = await conn.fetchrow("SELECT * FROM haken_moto_company LIMIT 1")
            if not company_row:
                raise HTTPException(
                    status_code=400,
                    detail="派遣元会社の情報が設定されていません。先に会社情報を登録してください。"
                )
            company = dict(company_row)
        except asyncpg.UndefinedTableError:
            raise HTTPException(
                status_code=500,
                detail="データベースの設定エラー: haken_moto_company テーブルが見つかりません"
            )

        # 3. Get Dispatch Data (Haken Saki) if available
        # This logic can be improved to get the *current* assignment
        dispatch_row = await conn.fetchrow("""
            SELECT hs.* 
            FROM dispatch_assignments da
            JOIN haken_saki_company hs ON da.haken_saki_id = hs.id
            WHERE da.employee_id = $1 AND da.assignment_status = 'active'
            LIMIT 1
        """, employee_id)
        
        haken_saki = dict(dispatch_row) if dispatch_row else {}
        
        # 4. Prepare Data for Generator
        # Map database fields to generator expected fields
        data = {
            # Basic Info
            "nationality": employee.get('nationality'),
            "date_of_birth": employee.get('date_of_birth'),
            "family_name": employee.get('family_name'),
            "given_name": employee.get('given_name'),
            "name_kanji": f"{employee.get('family_name_kanji', '')} {employee.get('given_name_kanji', '')}".strip(),
            "sex": employee.get('sex'),
            "marital_status": employee.get('marital_status'),
            "home_town_city": employee.get('home_town_city'),
            
            # Address
            "address_japan": employee.get('address_japan'),
            "telephone_japan": employee.get('telephone_japan'),
            "cellular_phone": employee.get('cellular_phone'),
            
            # Passport & Visa
            "passport_number": employee.get('passport_number'),
            "passport_expiration": employee.get('passport_expiration'),
            "current_visa_status": employee.get('current_visa_status'),
            "current_period_of_stay": employee.get('current_period_of_stay'),
            "current_expiration_date": employee.get('current_expiration_date'),
            "residence_card_number": employee.get('residence_card_number'),
            
            # Education
            "school_name": employee.get('school_name'),
            "graduation_date": employee.get('graduation_date'),
            "major_field": employee.get('major_field'),
            
            # Company (UNS)
            "employer_name": company.get('company_name'),
            "corporation_number": company.get('corporation_number'),
            "employer_address": company.get('full_address'),
            "employer_telephone": company.get('telephone'),
            "capital": company.get('capital'),
            "annual_sales": company.get('annual_sales'),
            "employee_count": company.get('total_employees'),
            "foreign_employee_count": company.get('foreign_employees'),
            "company_representative_name": company.get('representative_name'),
            
            # Dispatch (Haken Saki) - Used for work location
            "company_name": haken_saki.get('company_name'), # Work location name
            "company_address": haken_saki.get('full_address'),
            "company_telephone": haken_saki.get('telephone'),
        }
        
        # Generate Excel
        excel_file = generate_visa_renewal_excel(data)
        
        # Filename
        filename = f"visa_renewal_{employee.get('employee_code')}_{date.today()}.xlsx"
        
        # Return as stream
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )


@router.get("/visa-coe/{employee_id}")
async def export_visa_coe(employee_id: int):
    """
    在留資格認定証明書交付申請書をエクスポート
    Export Certificate of Eligibility Application Form (Excel)
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        # 1. Get Employee Data
        emp_row = await conn.fetchrow("SELECT * FROM employees WHERE id = $1", employee_id)
        if not emp_row:
            raise HTTPException(404, "従業員が見つかりません")

        employee = dict(emp_row)

        # 2. Get Company Data (UNS)
        try:
            company_row = await conn.fetchrow("SELECT * FROM haken_moto_company LIMIT 1")
            if not company_row:
                raise HTTPException(
                    status_code=400,
                    detail="派遣元会社の情報が設定されていません。先に会社情報を登録してください。"
                )
            company = dict(company_row)
        except asyncpg.UndefinedTableError:
            raise HTTPException(
                status_code=500,
                detail="データベースの設定エラー: haken_moto_company テーブルが見つかりません"
            )

        # 3. Get Dispatch Data (Haken Saki)
        dispatch_row = await conn.fetchrow(
            """
            SELECT hs.*
            FROM dispatch_assignments da
            JOIN haken_saki_company hs ON da.haken_saki_id = hs.id
            WHERE da.employee_id = $1 AND da.assignment_status = 'active'
            LIMIT 1
            """,
            employee_id,
        )

        haken_saki = dict(dispatch_row) if dispatch_row else {}

        # 4. Prepare Data
        data = {
            "nationality": employee.get("nationality"),
            "date_of_birth": employee.get("date_of_birth"),
            "family_name": employee.get("family_name"),
            "given_name": employee.get("given_name"),
            "name_kanji": f"{employee.get('family_name_kanji', '')} {employee.get('given_name_kanji', '')}".strip(),
            "sex": employee.get("sex"),
            "marital_status": employee.get("marital_status"),
            "home_town_city": employee.get("home_town_city"),
            "address_japan": employee.get("address_japan"),
            "telephone_japan": employee.get("telephone_japan"),
            "cellular_phone": employee.get("cellular_phone"),
            "passport_number": employee.get("passport_number"),
            "passport_expiration": employee.get("passport_expiration"),
            "current_visa_status": employee.get("current_visa_status"),
            "current_period_of_stay": employee.get("current_period_of_stay"),
            "current_expiration_date": employee.get("current_expiration_date"),
            "residence_card_number": employee.get("residence_card_number"),
            "school_name": employee.get("school_name"),
            "graduation_date": employee.get("graduation_date"),
            "major_field": employee.get("major_field"),
            "employer_name": company.get("company_name"),
            "corporation_number": company.get("corporation_number"),
            "employer_address": company.get("full_address"),
            "employer_telephone": company.get("telephone"),
            "capital": company.get("capital"),
            "annual_sales": company.get("annual_sales"),
            "employee_count": company.get("total_employees"),
            "foreign_employee_count": company.get("foreign_employees"),
            "company_representative_name": company.get("representative_name"),
            "company_name": haken_saki.get("company_name"),
            "company_address": haken_saki.get("full_address"),
            "company_telephone": haken_saki.get("telephone"),
            "form_type": "coe",
            "submission_office": employee.get("submission_office", "名古屋"),
        }

        generator = VisaFormExcelGenerator()
        excel_file = generator.generate_renewal_form(data)

        filename = f"visa_coe_{employee.get('employee_code')}_{date.today()}.xlsx"

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )


@router.get("/visa-change/{employee_id}")
async def export_visa_change(employee_id: int):
    """
    在留資格変更許可申請書をエクスポート
    Export Visa Status Change Application Form (Excel)
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        # 1. Get Employee Data
        emp_row = await conn.fetchrow("SELECT * FROM employees WHERE id = $1", employee_id)
        if not emp_row:
            raise HTTPException(404, "従業員が見つかりません")

        employee = dict(emp_row)

        # 2. Get Company Data (UNS)
        try:
            company_row = await conn.fetchrow("SELECT * FROM haken_moto_company LIMIT 1")
            if not company_row:
                raise HTTPException(
                    status_code=400,
                    detail="派遣元会社の情報が設定されていません。先に会社情報を登録してください。"
                )
            company = dict(company_row)
        except asyncpg.UndefinedTableError:
            raise HTTPException(
                status_code=500,
                detail="データベースの設定エラー: haken_moto_company テーブルが見つかりません"
            )

        # 3. Get Dispatch Data (Haken Saki)
        dispatch_row = await conn.fetchrow(
            """
            SELECT hs.*
            FROM dispatch_assignments da
            JOIN haken_saki_company hs ON da.haken_saki_id = hs.id
            WHERE da.employee_id = $1 AND da.assignment_status = 'active'
            LIMIT 1
            """,
            employee_id,
        )

        haken_saki = dict(dispatch_row) if dispatch_row else {}

        # 4. Prepare Data
        data = {
            "nationality": employee.get("nationality"),
            "date_of_birth": employee.get("date_of_birth"),
            "family_name": employee.get("family_name"),
            "given_name": employee.get("given_name"),
            "name_kanji": f"{employee.get('family_name_kanji', '')} {employee.get('given_name_kanji', '')}".strip(),
            "sex": employee.get("sex"),
            "marital_status": employee.get("marital_status"),
            "home_town_city": employee.get("home_town_city"),
            "address_japan": employee.get("address_japan"),
            "telephone_japan": employee.get("telephone_japan"),
            "cellular_phone": employee.get("cellular_phone"),
            "passport_number": employee.get("passport_number"),
            "passport_expiration": employee.get("passport_expiration"),
            "current_visa_status": employee.get("current_visa_status"),
            "current_period_of_stay": employee.get("current_period_of_stay"),
            "current_expiration_date": employee.get("current_expiration_date"),
            "residence_card_number": employee.get("residence_card_number"),
            "school_name": employee.get("school_name"),
            "graduation_date": employee.get("graduation_date"),
            "major_field": employee.get("major_field"),
            "employer_name": company.get("company_name"),
            "corporation_number": company.get("corporation_number"),
            "employer_address": company.get("full_address"),
            "employer_telephone": company.get("telephone"),
            "capital": company.get("capital"),
            "annual_sales": company.get("annual_sales"),
            "employee_count": company.get("total_employees"),
            "foreign_employee_count": company.get("foreign_employees"),
            "company_representative_name": company.get("representative_name"),
            "company_name": haken_saki.get("company_name"),
            "company_address": haken_saki.get("full_address"),
            "company_telephone": haken_saki.get("telephone"),
            "form_type": "change",  # Marcar como formulario de cambio
            "submission_office": employee.get("submission_office", "名古屋"),
        }

        generator = VisaFormExcelGenerator()
        excel_file = generator.generate_renewal_form(data)

        filename = f"visa_change_{employee.get('employee_code')}_{date.today()}.xlsx"

        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
