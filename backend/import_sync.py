"""
Importa empleados desde Excel y clientes (haken_saki) desde JSON de factories.
Ejemplo:
  python -m backend.import_sync --excel "D:\\JPUNS-Claude.6.5.0\\BASEDATEJP\\【新】社員台帳(UNS)T　2022.04.05～.xlsm" --sheet DBGenzaiX --factories "D:\\JPUNS-Claude.6.5.0\\BASEDATEJP\\config\\factories"
"""

import argparse
import asyncio
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import pandas as pd

from database import get_db_url


# -----------------------------------------
# Helpers generales
# -----------------------------------------

def to_str(val: Any) -> str:
    return "" if val is None or (isinstance(val, float) and pd.isna(val)) else str(val).strip()


def to_date(val: Any) -> Optional[date]:
    ts = pd.to_datetime(val, errors="coerce")
    return ts.date() if pd.notna(ts) else None


def split_name(full_name: str) -> Tuple[str, str]:
    if not full_name:
        return "", ""
    parts = re.split(r"\s+", full_name.strip())
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])
    return full_name, ""


def parse_prefecture(address: str) -> str:
    if not address:
        return ""
    m = re.match(r"^(北海道|東京都|京都府|大阪府|..県|..府|..都)", address)
    return m.group(1) if m else ""


# -----------------------------------------
# Empleados
# -----------------------------------------

EMPLOYEE_COLUMNS = {
    "現在": "employment_status",
    "社員№": "employee_code",
    "氏名": "name",
    "性別": "sex",
    "国籍": "nationality",
    "生年月日": "date_of_birth",
    "ビザ期限": "current_expiration_date",
    "ビザ種類": "current_visa_status",
    "〒": "postal_code_japan",
    "住所": "address",
    "ｱﾊﾟｰﾄ": "apartment",
    "入社日": "hire_date",
    "退社日": "termination_date",
}


def normalize_employee_row(row: pd.Series) -> Dict[str, Any]:
    raw_name = to_str(row.get("氏名"))
    family_name, given_name = split_name(raw_name)
    address = to_str(row.get("住所"))
    apt = to_str(row.get("ｱﾊﾟｰﾄ"))
    full_address = f"{address} {apt}".strip() if apt else address

    sex_raw = to_str(row.get("性別"))
    sex = ""
    if sex_raw in ("男", "男性", "M", "1"):
        sex = "male"
    elif sex_raw in ("女", "女性", "F", "2"):
        sex = "female"

    employment_status_raw = to_str(row.get("現在"))
    employment_status = "inactive" if employment_status_raw == "退社" else "active"

    return {
        "employee_code": to_str(row.get("社員№")),
        "family_name": family_name,
        "given_name": given_name,
        "family_name_kanji": family_name,
        "given_name_kanji": given_name,
        "nationality": to_str(row.get("国籍")),
        "date_of_birth": to_date(row.get("生年月日")),
        "sex": sex,
        "postal_code_japan": to_str(row.get("〒")).replace("-", ""),
        "address_japan": full_address,
        "current_visa_status": to_str(row.get("ビザ種類")),
        "current_expiration_date": to_date(row.get("ビザ期限")),
        "hire_date": to_date(row.get("入社日")),
        "termination_date": to_date(row.get("退社日")),
        "employment_status": employment_status,
    }


async def upsert_employees(pool: asyncpg.Pool, employees: List[Dict[str, Any]]) -> Tuple[int, int]:
    created = 0
    updated = 0
    if not employees:
        return created, updated

    async with pool.acquire() as conn:
        for emp in employees:
            if not emp["employee_code"]:
                continue
            query = """
                INSERT INTO employees (
                    employee_code, family_name, given_name, family_name_kanji, given_name_kanji,
                    nationality, date_of_birth, sex, postal_code_japan, address_japan,
                    current_visa_status, current_expiration_date, hire_date, termination_date,
                    employment_status
                ) VALUES (
                    $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15
                )
                ON CONFLICT (employee_code) DO UPDATE SET
                    family_name = EXCLUDED.family_name,
                    given_name = EXCLUDED.given_name,
                    family_name_kanji = EXCLUDED.family_name_kanji,
                    given_name_kanji = EXCLUDED.given_name_kanji,
                    nationality = EXCLUDED.nationality,
                    date_of_birth = EXCLUDED.date_of_birth,
                    sex = EXCLUDED.sex,
                    postal_code_japan = EXCLUDED.postal_code_japan,
                    address_japan = EXCLUDED.address_japan,
                    current_visa_status = EXCLUDED.current_visa_status,
                    current_expiration_date = EXCLUDED.current_expiration_date,
                    hire_date = EXCLUDED.hire_date,
                    termination_date = EXCLUDED.termination_date,
                    employment_status = EXCLUDED.employment_status
                RETURNING (xmax = 0) AS inserted
            """
            res = await conn.fetchrow(
                query,
                emp["employee_code"],
                emp["family_name"],
                emp["given_name"],
                emp["family_name_kanji"],
                emp["given_name_kanji"],
                emp["nationality"],
                emp["date_of_birth"],
                emp["sex"],
                emp["postal_code_japan"],
                emp["address_japan"],
                emp["current_visa_status"],
                emp["current_expiration_date"],
                emp["hire_date"],
                emp["termination_date"],
                emp["employment_status"],
            )
            if res and res["inserted"]:
                created += 1
            else:
                updated += 1

    return created, updated


def load_employees_from_excel(path: Path, sheet: str) -> List[Dict[str, Any]]:
    df = pd.read_excel(path, sheet_name=sheet)
    missing_cols = [c for c in EMPLOYEE_COLUMNS.keys() if c not in df.columns]
    if missing_cols:
        print(f"Advertencia: faltan columnas en Excel: {missing_cols}")
    employees = []
    for _, row in df.iterrows():
        emp = normalize_employee_row(row)
        if emp["employee_code"]:
            employees.append(emp)
    return employees


# -----------------------------------------
# Factories -> haken_saki_company
# -----------------------------------------

def normalize_factory(factory: Dict[str, Any]) -> Dict[str, Any]:
    client = factory.get("client_company", {}) or {}
    plant = factory.get("plant", {}) or {}
    company_name = to_str(client.get("name"))
    branch_name = to_str(plant.get("name"))
    full_address = to_str(plant.get("address")) or to_str(client.get("address"))
    telephone = to_str(plant.get("phone")) or to_str(client.get("phone"))
    contact_person = to_str(client.get("responsible_person", {}).get("name"))
    prefecture = parse_prefecture(full_address)

    return {
        "company_name": company_name,
        "branch_name": branch_name,
        "corporation_number": to_str(client.get("corporation_number")),
        "employment_insurance_number": to_str(client.get("employment_insurance_number")),
        "full_address": full_address,
        "prefecture": prefecture,
        "telephone": telephone,
        "contact_person": contact_person,
    }


async def insert_haken_saki(pool: asyncpg.Pool, factories: List[Dict[str, Any]]) -> Tuple[int, int]:
    created = 0
    skipped = 0
    if not factories:
        return created, skipped

    async with pool.acquire() as conn:
        for f in factories:
            corp = f.get("corporation_number") or None
            if corp:
                existing = await conn.fetchval(
                    "SELECT id FROM haken_saki_company WHERE corporation_number = $1 LIMIT 1",
                    corp,
                )
            else:
                existing = await conn.fetchval(
                    """
                    SELECT id FROM haken_saki_company
                    WHERE company_name = $1 AND COALESCE(prefecture,'') = COALESCE($2,'')
                    LIMIT 1
                    """,
                    f["company_name"],
                    f["prefecture"],
                )
            if existing:
                skipped += 1
                continue

            await conn.execute(
                """
                INSERT INTO haken_saki_company (
                    company_name, branch_name, corporation_number, employment_insurance_number,
                    full_address, prefecture, telephone, contact_person
                ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                """,
                f["company_name"],
                f["branch_name"],
                corp,
                f.get("employment_insurance_number") or None,
                f["full_address"],
                f["prefecture"],
                f["telephone"],
                f["contact_person"],
            )
            created += 1

    return created, skipped


def load_factories(path: Path) -> List[Dict[str, Any]]:
    factories: List[Dict[str, Any]] = []
    for file in sorted(path.glob("*.json")):
        with file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        factories.append(normalize_factory(data))
    return factories


# -----------------------------------------
# Main
# -----------------------------------------

async def main():
    parser = argparse.ArgumentParser(description="Sincroniza empleados y factories en la base de datos.")
    parser.add_argument("--excel", required=True, help="Ruta al Excel de empleados")
    parser.add_argument("--sheet", default="DBGenzaiX", help="Nombre de la hoja (default DBGenzaiX)")
    parser.add_argument("--factories", required=True, help="Carpeta con factories/*.json")
    parser.add_argument("--db-url", default=None, help="URL de la base (override DATABASE_URL)")
    args = parser.parse_args()

    excel_path = Path(args.excel)
    factories_path = Path(args.factories)

    if not excel_path.exists():
        raise SystemExit(f"No existe el Excel: {excel_path}")
    if not factories_path.exists() or not factories_path.is_dir():
        raise SystemExit(f"No existe la carpeta de factories: {factories_path}")

    print(f"Excel: {excel_path}")
    print(f"Factories dir: {factories_path}")
    print(f"Sheet: {args.sheet}")

    employees = load_employees_from_excel(excel_path, args.sheet)
    factories = load_factories(factories_path)
    print(f"Empleados leídos: {len(employees)}")
    print(f"Factories leídos: {len(factories)}")

    db_url = args.db_url or get_db_url()
    print(f"DB URL: {db_url}")
    pool = await asyncpg.create_pool(db_url)

    emp_created, emp_updated = await upsert_employees(pool, employees)
    print(f"Empleados -> creados: {emp_created}, actualizados: {emp_updated}")

    fac_created, fac_skipped = await insert_haken_saki(pool, factories)
    print(f"Factories -> creados: {fac_created}, omitidos (duplicados): {fac_skipped}")

    await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
