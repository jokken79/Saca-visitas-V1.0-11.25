#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir datos de factories y empleados al formato del sistema UNS
"""

import json
import pandas as pd
import sys
from pathlib import Path

def convert_factory_to_haken_saki(factory_file):
    """Convertir archivo JSON de factory a formato haken-saki"""
    
    print(f"Procesando factory: {factory_file}")
    
    with open(factory_file, 'r', encoding='utf-8') as f:
        factory_data = json.load(f)
    
    # Extraer información principal
    client = factory_data.get('client_company', {})
    plant = factory_data.get('plant', {})
    
    # Mapear al formato del sistema
    haken_saki = {
        "company_name": client.get('name', ''),
        "branch_name": plant.get('name', ''),
        "corporation_number": "",  # No disponible en el formato original
        "employment_insurance_number": "",  # No disponible
        "postal_code": "",  # Extraer de dirección si es necesario
        "prefecture": "",  # Extraer de dirección
        "city": "",  # Extraer de dirección
        "address_line1": plant.get('address', ''),
        "full_address": plant.get('address', ''),
        "telephone": plant.get('phone', ''),
        "fax": "",  # No disponible
        "contact_person": client.get('responsible_person', {}).get('name', ''),
        "contact_email": "",  # No disponible
        "capital": 0,  # No disponible
        "annual_sales": 0,  # No disponible
        "total_employees": 0,  # No disponible
        "foreign_employees": 0,  # No disponible
        "business_type_code": "",  # No disponible
        "business_type_name": "製造業"  # Por defecto
    }
    
    return [haken_saki]

def convert_excel_to_employees(excel_file, sheet_name='DBGenzaiX'):
    """Convertir archivo Excel de empleados al formato del sistema"""
    
    print(f"Procesando Excel: {excel_file}")
    
    try:
        # Leer el archivo Excel
        xl = pd.ExcelFile(excel_file)
        
        # Verificar si existe la hoja DBGenzaiX
        if sheet_name not in xl.sheet_names:
            print(f"Hoja '{sheet_name}' no encontrada. Hojas disponibles: {xl.sheet_names}")
            # Usar la primera hoja disponible
            sheet_name = xl.sheet_names[0]
            print(f"Usando hoja: {sheet_name}")
        
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        print(f"Columnas encontradas: {list(df.columns)}")
        print(f"Filas totales: {len(df)}")
        
        employees = []
        
        for index, row in df.iterrows():
            # Mapeo de columnas - ajustar según el formato real
            employee = {
                "employee_code": str(row.get('社員番号', '')) if pd.notna(row.get('社員番号')) else '',
                "family_name": str(row.get('姓', '')) if pd.notna(row.get('姓')) else '',
                "given_name": str(row.get('名', '')) if pd.notna(row.get('名')) else '',
                "family_name_kanji": str(row.get('漢字氏名', '')).split()[0] if pd.notna(row.get('漢字氏名')) and ' ' in str(row.get('漢字氏名')) else str(row.get('漢字氏名', '')).split()[0] if pd.notna(row.get('漢字氏名')) else '',
                "given_name_kanji": str(row.get('漢字氏名', '')).split()[-1] if pd.notna(row.get('漢字氏名')) and ' ' in str(row.get('漢字氏名')) else str(row.get('漢字氏名', '')).split()[-1] if pd.notna(row.get('漢字氏名')) else '',
                "nationality": str(row.get('国籍', '')) if pd.notna(row.get('国籍')) else '',
                "date_of_birth": str(row.get('生年月日', '')) if pd.notna(row.get('生年月日')) else '',
                "sex": 'male' if str(row.get('性別', '')).strip() in ['男', '男性', 'M', '1'] else 'female' if str(row.get('性別', '')).strip() in ['女', '女性', 'F', '2'] else '',
                "passport_number": str(row.get('パスポート番号', '')) if pd.notna(row.get('パスポート番号')) else '',
                "passport_expiration": str(row.get('パスポート有効期限', '')) if pd.notna(row.get('パスポート有効期限')) else '',
                "current_visa_status": str(row.get('在留資格', '')) if pd.notna(row.get('在留資格')) else '',
                "current_period_of_stay": str(row.get('在留期間', '')) if pd.notna(row.get('在留期間')) else '',
                "current_expiration_date": str(row.get('在留期限', '')) if pd.notna(row.get('在留期限')) else '',
                "residence_card_number": str(row.get('在留カード番号', '')) if pd.notna(row.get('在留カード番号')) else '',
                "postal_code_japan": str(row.get('郵便番号', '')) if pd.notna(row.get('郵便番号')) else '',
                "address_japan": str(row.get('住所', '')) if pd.notna(row.get('住所')) else '',
                "telephone_japan": str(row.get('電話番号', '')) if pd.notna(row.get('電話番号')) else '',
                "cellular_phone": str(row.get('携帯電話', '')) if pd.notna(row.get('携帯電話')) else '',
                "email": str(row.get('メール', '')) if pd.notna(row.get('メール')) else ''
            }
            
            employees.append(employee)
        
        print(f"Se procesaron {len(employees)} empleados")
        return employees
        
    except Exception as e:
        print(f"Error procesando Excel: {e}")
        return []

def main():
    """Función principal"""
    
    # Rutas de los archivos
    factory_file = r"D:\JPUNS-Claude.6.5.0\config\factories\高雄工業株式会社_海南第一工場.json"
    excel_file = r"D:\JPUNS-Claude.6.5.0\BASEDATEJP\【新】社員台帳(UNS)T　2022.04.05～.xlsm"
    
    # Convertir factory
    print("=== CONVIRTIENDO FACTORY ===")
    try:
        haken_saki_data = convert_factory_to_haken_saki(factory_file)
        
        # Guardar archivo convertido
        output_factory = "haken_saki_import.json"
        with open(output_factory, 'w', encoding='utf-8') as f:
            json.dump(haken_saki_data, f, ensure_ascii=False, indent=2)
        
        print(f"OK Factory guardado en: {output_factory}")
        
    except Exception as e:
        print(f"ERROR procesando factory: {e}")
    
    # Convertir empleados
    print("\n=== CONVIRTIENDO EMPLEADOS ===")
    try:
        employees_data = convert_excel_to_employees(excel_file)
        
        if employees_data:
            # Guardar como Excel para importación
            output_excel = "employees_import.xlsx"
            
            # Crear DataFrame
            df = pd.DataFrame(employees_data)
            
            # Guardar como Excel
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='従業員データ', index=False)
            
            print(f"OK Empleados guardados en: {output_excel}")
            
            # También guardar como JSON para referencia
            output_json = "employees_import.json"
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(employees_data, f, ensure_ascii=False, indent=2)
            print(f"OK Empleados también guardados en: {output_json}")
        
    except Exception as e:
        print(f"ERROR procesando empleados: {e}")
    
    print("\n=== PROCESO COMPLETADO ===")
    print("Archivos generados:")
    print("- haken_saki_import.json (para importar factories)")
    print("- employees_import.xlsx (para importar empleados)")

if __name__ == "__main__":
    main()