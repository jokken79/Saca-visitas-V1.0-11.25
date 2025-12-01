-- ============================================================
-- UNS VISA MANAGEMENT SYSTEM
-- Database Initialization Script
-- PostgreSQL 15
-- ============================================================

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para búsquedas de texto

-- ============================================================
-- TABLA 1: 派遣元会社 (HAKEN MOTO - Tu empresa UNS)
-- ============================================================
CREATE TABLE IF NOT EXISTS haken_moto_company (
    id SERIAL PRIMARY KEY,
    
    -- Información básica
    company_name VARCHAR(200) NOT NULL,
    company_name_kana VARCHAR(200),
    company_name_en VARCHAR(200),
    
    -- Números de registro oficiales
    corporation_number VARCHAR(13) UNIQUE,
    employment_insurance_number VARCHAR(11),
    worker_dispatch_license VARCHAR(50),
    
    -- Dirección
    postal_code VARCHAR(8),
    prefecture VARCHAR(20),
    city VARCHAR(50),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    full_address TEXT,
    
    -- Contacto
    telephone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(200),
    
    -- Información financiera
    capital BIGINT,
    annual_sales BIGINT,
    fiscal_year_end VARCHAR(10),
    
    -- Empleados
    total_employees INT,
    japanese_employees INT,
    foreign_employees INT,
    
    -- Representante
    representative_name VARCHAR(100),
    representative_title VARCHAR(50),
    representative_name_kana VARCHAR(100),
    
    -- Negocio
    business_type_code VARCHAR(10),
    business_type_name VARCHAR(100),
    main_business_description TEXT,
    
    -- Categoría入管
    immigration_category INT CHECK (immigration_category IN (1,2,3,4)),
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- TABLA 2: 派遣先会社 (HAKEN SAKI - Fábricas/Clientes)
-- ============================================================
CREATE TABLE IF NOT EXISTS haken_saki_company (
    id SERIAL PRIMARY KEY,
    
    -- Información básica
    company_name VARCHAR(200) NOT NULL,
    company_name_kana VARCHAR(200),
    branch_name VARCHAR(100),
    
    -- Números de registro
    corporation_number VARCHAR(13),
    employment_insurance_number VARCHAR(11),
    
    -- Dirección
    postal_code VARCHAR(8),
    prefecture VARCHAR(20),
    city VARCHAR(50),
    address_line1 VARCHAR(200),
    address_line2 VARCHAR(200),
    full_address TEXT,
    
    -- Contacto
    telephone VARCHAR(20),
    fax VARCHAR(20),
    contact_person VARCHAR(100),
    contact_email VARCHAR(100),
    
    -- Información financiera
    capital BIGINT,
    annual_sales BIGINT,
    
    -- Empleados
    total_employees INT,
    foreign_employees INT,
    trainee_count INT DEFAULT 0,
    
    -- Negocio
    business_type_code VARCHAR(10),
    business_type_name VARCHAR(100),
    industry_sector VARCHAR(100),
    
    -- Contrato
    contract_start_date DATE,
    contract_end_date DATE,
    contract_status VARCHAR(20) DEFAULT 'active',
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- ============================================================
-- TABLA 3: 従業員 (EMPLOYEES - Trabajadores extranjeros)
-- ============================================================
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE,
    
    -- ===== INFORMACIÓN PERSONAL =====
    family_name VARCHAR(100) NOT NULL,
    given_name VARCHAR(100) NOT NULL,
    family_name_kanji VARCHAR(100),
    given_name_kanji VARCHAR(100),
    name_kana VARCHAR(200),
    
    nationality VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    sex VARCHAR(10) CHECK (sex IN ('male', 'female')),
    place_of_birth VARCHAR(100),
    marital_status VARCHAR(20) CHECK (marital_status IN ('married', 'single', 'divorced', 'widowed')),
    home_town_city VARCHAR(200),
    
    -- Foto
    photo_url VARCHAR(500),
    photo_taken_date DATE,
    
    -- ===== CONTACTO EN JAPÓN =====
    postal_code_japan VARCHAR(8),
    address_japan TEXT,
    telephone_japan VARCHAR(20),
    cellular_phone VARCHAR(20),
    email VARCHAR(100),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    
    -- ===== PASAPORTE =====
    passport_number VARCHAR(20),
    passport_expiration DATE,
    passport_issue_country VARCHAR(100),
    passport_issue_date DATE,
    
    -- ===== 在留資格 (VISA) =====
    current_visa_status VARCHAR(100),
    current_period_of_stay VARCHAR(20),
    current_expiration_date DATE,
    residence_card_number VARCHAR(20),
    residence_card_expiration DATE,
    
    -- Historial
    first_entry_date DATE,
    total_years_in_japan DECIMAL(4,1),
    
    -- ===== EDUCACIÓN =====
    education_level VARCHAR(50),
    school_location VARCHAR(20),
    school_name VARCHAR(200),
    school_country VARCHAR(100),
    graduation_date DATE,
    major_field VARCHAR(100),
    major_field_code VARCHAR(10),
    degree_obtained VARCHAR(100),
    
    -- IT
    has_it_qualification BOOLEAN DEFAULT FALSE,
    it_qualification_name VARCHAR(200),
    it_qualification_date DATE,
    
    -- Otras calificaciones
    other_qualifications TEXT,
    japanese_level VARCHAR(20),
    japanese_certification_date DATE,
    
    -- ===== HISTORIAL CRIMINAL/DEPORTACIÓN =====
    has_criminal_record BOOLEAN DEFAULT FALSE,
    criminal_record_details TEXT,
    has_deportation_history BOOLEAN DEFAULT FALSE,
    deportation_count INT DEFAULT 0,
    latest_deportation_date DATE,
    
    -- ===== ESTADO LABORAL =====
    employment_status VARCHAR(30) DEFAULT 'active',
    hire_date DATE,
    termination_date DATE,
    termination_reason TEXT,
    
    -- ===== METADATOS =====
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    updated_by INT,
    notes TEXT
);

-- ============================================================
-- TABLA 4: 雇用契約 (EMPLOYMENT CONTRACTS)
-- ============================================================
CREATE TABLE IF NOT EXISTS employment_contracts (
    id SERIAL PRIMARY KEY,
    
    employee_id INT REFERENCES employees(id) ON DELETE CASCADE,
    haken_moto_id INT REFERENCES haken_moto_company(id),
    
    -- Contrato
    contract_number VARCHAR(50) UNIQUE,
    contract_type VARCHAR(30),
    employment_type VARCHAR(30),
    
    -- Período
    contract_start_date DATE NOT NULL,
    contract_end_date DATE,
    is_indefinite BOOLEAN DEFAULT FALSE,
    probation_period_months INT,
    
    -- Salario
    salary_amount BIGINT NOT NULL,
    salary_type VARCHAR(20) CHECK (salary_type IN ('monthly', 'yearly', 'hourly', 'daily')),
    salary_before_tax BOOLEAN DEFAULT TRUE,
    bonus_description TEXT,
    allowances TEXT,
    
    -- Horario
    working_hours_per_week DECIMAL(4,1),
    work_days_per_week INT,
    work_schedule_description TEXT,
    
    -- Posición
    position_title VARCHAR(100),
    occupation_code VARCHAR(10),
    occupation_name VARCHAR(100),
    activity_details TEXT,
    
    -- Experiencia
    business_experience_years DECIMAL(4,1),
    
    -- Estado
    contract_status VARCHAR(20) DEFAULT 'active',
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_url VARCHAR(500)
);

-- ============================================================
-- TABLA 5: 派遣契約 (DISPATCH ASSIGNMENTS)
-- ============================================================
CREATE TABLE IF NOT EXISTS dispatch_assignments (
    id SERIAL PRIMARY KEY,
    
    employee_id INT REFERENCES employees(id) ON DELETE CASCADE,
    employment_contract_id INT REFERENCES employment_contracts(id),
    haken_saki_id INT REFERENCES haken_saki_company(id),
    
    -- Período
    dispatch_start_date DATE NOT NULL,
    dispatch_end_date DATE,
    dispatch_period_description VARCHAR(50),
    
    -- Lugar de trabajo
    work_location_address TEXT,
    work_location_department VARCHAR(100),
    
    -- Trabajo
    job_title VARCHAR(100),
    job_description TEXT,
    supervisor_name VARCHAR(100),
    supervisor_position VARCHAR(100),
    
    -- Horario
    work_start_time TIME,
    work_end_time TIME,
    break_time_minutes INT,
    
    -- Estado
    assignment_status VARCHAR(20) DEFAULT 'active',
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- ============================================================
-- TABLA 6: 家族情報 (EMPLOYEE FAMILY)
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_family (
    id SERIAL PRIMARY KEY,
    
    employee_id INT REFERENCES employees(id) ON DELETE CASCADE,
    
    -- Información
    relationship VARCHAR(30),
    family_name VARCHAR(100),
    given_name VARCHAR(100),
    date_of_birth DATE,
    nationality VARCHAR(100),
    
    -- Residencia
    is_residing_together BOOLEAN DEFAULT FALSE,
    address_if_different TEXT,
    
    -- Trabajo/Escuela
    place_of_employment VARCHAR(200),
    occupation VARCHAR(100),
    
    -- Visa
    residence_card_number VARCHAR(20),
    visa_status VARCHAR(100),
    visa_expiration DATE,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA 7: 職歴 (WORK HISTORY)
-- ============================================================
CREATE TABLE IF NOT EXISTS employee_work_history (
    id SERIAL PRIMARY KEY,
    
    employee_id INT REFERENCES employees(id) ON DELETE CASCADE,
    
    -- Empleo anterior
    company_name VARCHAR(200) NOT NULL,
    company_country VARCHAR(100),
    
    -- Período
    start_date DATE,
    end_date DATE,
    period_description VARCHAR(100),
    
    -- Posición
    position_title VARCHAR(100),
    department VARCHAR(100),
    job_description TEXT,
    
    -- Orden
    display_order INT,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA 8: ビザ申請 (VISA APPLICATIONS)
-- ============================================================
CREATE TABLE IF NOT EXISTS visa_applications (
    id SERIAL PRIMARY KEY,
    
    employee_id INT REFERENCES employees(id) ON DELETE CASCADE,
    employment_contract_id INT REFERENCES employment_contracts(id),
    dispatch_assignment_id INT REFERENCES dispatch_assignments(id),
    
    -- Tipo
    application_type VARCHAR(50) NOT NULL,
    visa_category VARCHAR(100),
    
    -- Solicitud
    submission_office VARCHAR(100),
    application_date DATE,
    application_number VARCHAR(50),
    
    -- Período solicitado
    requested_period VARCHAR(20),
    reason_for_application TEXT,
    
    -- Representante
    representative_type VARCHAR(30),
    representative_name VARCHAR(100),
    representative_organization VARCHAR(200),
    
    -- Estado
    application_status VARCHAR(30) DEFAULT 'draft',
    
    -- Resultado
    decision_date DATE,
    approved_period VARCHAR(20),
    new_expiration_date DATE,
    denial_reason TEXT,
    
    -- Documentos
    excel_file_url VARCHAR(500),
    pdf_file_url VARCHAR(500),
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INT,
    submitted_by INT,
    notes TEXT
);

-- ============================================================
-- TABLA 9: 申請書類 (APPLICATION DOCUMENTS)
-- ============================================================
CREATE TABLE IF NOT EXISTS application_documents (
    id SERIAL PRIMARY KEY,
    
    visa_application_id INT REFERENCES visa_applications(id) ON DELETE CASCADE,
    
    document_type VARCHAR(100),
    document_name VARCHAR(200),
    file_url VARCHAR(500),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    
    is_required BOOLEAN DEFAULT TRUE,
    is_submitted BOOLEAN DEFAULT FALSE,
    submitted_date DATE,
    
    -- Metadatos
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INT,
    notes TEXT
);

-- ============================================================
-- TABLA 10: 通知 (NOTIFICATIONS)
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    
    employee_id INT REFERENCES employees(id) ON DELETE CASCADE,
    visa_application_id INT REFERENCES visa_applications(id),
    
    notification_type VARCHAR(50),
    title VARCHAR(200),
    message TEXT,
    
    due_date DATE,
    days_before_due INT,
    
    is_read BOOLEAN DEFAULT FALSE,
    is_actioned BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    actioned_at TIMESTAMP
);

-- ============================================================
-- TABLA 11: 監査ログ (AUDIT LOG)
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    
    table_name VARCHAR(100),
    record_id INT,
    action VARCHAR(20),
    old_values JSONB,
    new_values JSONB,
    
    user_id INT,
    user_name VARCHAR(100),
    ip_address VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLA 12: ユーザー (USERS - Sistema)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    full_name VARCHAR(100),
    role VARCHAR(30) DEFAULT 'staff',
    
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ÍNDICES
-- ============================================================

-- Employees
CREATE INDEX idx_employees_nationality ON employees(nationality);
CREATE INDEX idx_employees_visa_expiration ON employees(current_expiration_date);
CREATE INDEX idx_employees_status ON employees(employment_status);
CREATE INDEX idx_employees_residence_card ON employees(residence_card_number);
CREATE INDEX idx_employees_name ON employees(family_name, given_name);
CREATE INDEX idx_employees_code ON employees(employee_code);

-- Contracts
CREATE INDEX idx_contracts_employee ON employment_contracts(employee_id);
CREATE INDEX idx_contracts_status ON employment_contracts(contract_status);
CREATE INDEX idx_contracts_dates ON employment_contracts(contract_start_date, contract_end_date);

-- Dispatch
CREATE INDEX idx_dispatch_employee ON dispatch_assignments(employee_id);
CREATE INDEX idx_dispatch_haken_saki ON dispatch_assignments(haken_saki_id);
CREATE INDEX idx_dispatch_dates ON dispatch_assignments(dispatch_start_date, dispatch_end_date);
CREATE INDEX idx_dispatch_status ON dispatch_assignments(assignment_status);

-- Visa Applications
CREATE INDEX idx_visa_apps_employee ON visa_applications(employee_id);
CREATE INDEX idx_visa_apps_status ON visa_applications(application_status);
CREATE INDEX idx_visa_apps_type ON visa_applications(application_type);
CREATE INDEX idx_visa_apps_date ON visa_applications(application_date);

-- Companies
CREATE INDEX idx_haken_saki_name ON haken_saki_company(company_name);
CREATE INDEX idx_haken_saki_status ON haken_saki_company(contract_status);
CREATE INDEX idx_haken_saki_active ON haken_saki_company(is_active);
CREATE INDEX idx_haken_saki_prefecture ON haken_saki_company(prefecture);

-- Users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- Full-text search (Japanese)
CREATE INDEX idx_haken_saki_name_trgm ON haken_saki_company USING gin(company_name gin_trgm_ops);
CREATE INDEX idx_employees_name_trgm ON employees USING gin(family_name gin_trgm_ops);

-- ============================================================
-- VISTAS
-- ============================================================

-- Vista: Empleados con visa por vencer
CREATE OR REPLACE VIEW v_employees_visa_expiring AS
SELECT 
    e.id,
    e.employee_code,
    e.family_name || ' ' || e.given_name AS full_name,
    e.family_name_kanji || ' ' || e.given_name_kanji AS full_name_kanji,
    e.nationality,
    e.current_visa_status,
    e.current_period_of_stay,
    e.current_expiration_date,
    (e.current_expiration_date - CURRENT_DATE) AS days_until_expiration,
    e.residence_card_number,
    e.cellular_phone,
    e.email,
    ec.position_title,
    ec.salary_amount,
    hs.company_name AS haken_saki_name,
    hs.full_address AS haken_saki_address,
    CASE 
        WHEN (e.current_expiration_date - CURRENT_DATE) < 0 THEN 'expired'
        WHEN (e.current_expiration_date - CURRENT_DATE) <= 30 THEN 'critical'
        WHEN (e.current_expiration_date - CURRENT_DATE) <= 60 THEN 'warning'
        WHEN (e.current_expiration_date - CURRENT_DATE) <= 90 THEN 'soon'
        ELSE 'ok'
    END AS visa_status
FROM employees e
LEFT JOIN employment_contracts ec ON e.id = ec.employee_id AND ec.contract_status = 'active'
LEFT JOIN dispatch_assignments da ON e.id = da.employee_id AND da.assignment_status = 'active'
LEFT JOIN haken_saki_company hs ON da.haken_saki_id = hs.id
WHERE e.employment_status = 'active'
ORDER BY e.current_expiration_date;

-- Vista: Empleados por派遣先
CREATE OR REPLACE VIEW v_employees_by_haken_saki AS
SELECT 
    hs.id AS haken_saki_id,
    hs.company_name AS haken_saki_name,
    hs.branch_name,
    hs.full_address,
    hs.telephone,
    hs.contact_person,
    COUNT(DISTINCT da.employee_id) AS active_employees,
    STRING_AGG(DISTINCT e.nationality, ', ' ORDER BY e.nationality) AS nationalities,
    MIN(e.current_expiration_date) AS nearest_visa_expiration
FROM haken_saki_company hs
LEFT JOIN dispatch_assignments da ON hs.id = da.haken_saki_id AND da.assignment_status = 'active'
LEFT JOIN employees e ON da.employee_id = e.id AND e.employment_status = 'active'
WHERE hs.is_active = TRUE
GROUP BY hs.id, hs.company_name, hs.branch_name, hs.full_address, hs.telephone, hs.contact_person
ORDER BY hs.company_name;

-- Vista: Datos completos para formulario de visa
CREATE OR REPLACE VIEW v_visa_form_data AS
SELECT 
    -- Datos del empleado
    e.id AS employee_id,
    e.employee_code,
    e.family_name,
    e.given_name,
    e.family_name_kanji,
    e.given_name_kanji,
    e.name_kana,
    e.nationality,
    e.date_of_birth,
    e.sex,
    e.place_of_birth,
    e.marital_status,
    e.home_town_city,
    e.postal_code_japan,
    e.address_japan,
    e.telephone_japan,
    e.cellular_phone,
    e.email,
    e.passport_number,
    e.passport_expiration,
    e.passport_issue_country,
    e.passport_issue_date,
    e.current_visa_status,
    e.current_period_of_stay,
    e.current_expiration_date,
    e.residence_card_number,
    e.education_level,
    e.school_location,
    e.school_name,
    e.graduation_date,
    e.major_field,
    e.has_it_qualification,
    e.it_qualification_name,
    e.japanese_level,
    e.has_criminal_record,
    e.criminal_record_details,
    
    -- Datos del contrato
    ec.id AS contract_id,
    ec.contract_type,
    ec.contract_start_date AS employment_start_date,
    ec.contract_end_date,
    ec.is_indefinite,
    ec.salary_amount,
    ec.salary_type,
    ec.position_title,
    ec.occupation_code,
    ec.occupation_name,
    ec.activity_details,
    ec.business_experience_years,
    
    -- Datos de派遣元
    hm.id AS haken_moto_id,
    hm.company_name AS haken_moto_name,
    hm.company_name_kana AS haken_moto_name_kana,
    hm.corporation_number AS haken_moto_corp_number,
    hm.employment_insurance_number AS haken_moto_insurance_number,
    hm.worker_dispatch_license AS haken_moto_dispatch_license,
    hm.full_address AS haken_moto_address,
    hm.telephone AS haken_moto_telephone,
    hm.capital AS haken_moto_capital,
    hm.annual_sales AS haken_moto_sales,
    hm.total_employees AS haken_moto_employees,
    hm.foreign_employees AS haken_moto_foreign_employees,
    hm.business_type_code AS haken_moto_business_code,
    hm.business_type_name AS haken_moto_business_name,
    hm.representative_name AS haken_moto_representative,
    hm.representative_title AS haken_moto_representative_title,
    hm.immigration_category,
    
    -- Datos de派遣
    da.id AS dispatch_id,
    da.dispatch_start_date,
    da.dispatch_end_date,
    da.dispatch_period_description,
    da.job_title AS dispatch_job_title,
    da.job_description AS dispatch_job_description,
    
    -- Datos de派遣先
    hs.id AS haken_saki_id,
    hs.company_name AS haken_saki_name,
    hs.branch_name AS haken_saki_branch,
    hs.corporation_number AS haken_saki_corp_number,
    hs.employment_insurance_number AS haken_saki_insurance_number,
    hs.full_address AS haken_saki_address,
    hs.telephone AS haken_saki_telephone,
    hs.capital AS haken_saki_capital,
    hs.annual_sales AS haken_saki_sales,
    hs.total_employees AS haken_saki_employees,
    hs.business_type_code AS haken_saki_business_code,
    hs.business_type_name AS haken_saki_business_name
    
FROM employees e
LEFT JOIN employment_contracts ec ON e.id = ec.employee_id AND ec.contract_status = 'active'
LEFT JOIN haken_moto_company hm ON ec.haken_moto_id = hm.id
LEFT JOIN dispatch_assignments da ON e.id = da.employee_id AND da.assignment_status = 'active'
LEFT JOIN haken_saki_company hs ON da.haken_saki_id = hs.id
WHERE e.employment_status = 'active';

-- Vista: Estadísticas del dashboard
CREATE OR REPLACE VIEW v_dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM employees WHERE employment_status = 'active') AS total_employees,
    (SELECT COUNT(*) FROM employees WHERE employment_status = 'active' 
     AND current_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days') AS expiring_30_days,
    (SELECT COUNT(*) FROM employees WHERE employment_status = 'active' 
     AND current_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days') AS expiring_90_days,
    (SELECT COUNT(*) FROM employees WHERE employment_status = 'active' 
     AND current_expiration_date < CURRENT_DATE) AS expired,
    (SELECT COUNT(*) FROM haken_saki_company WHERE is_active = TRUE) AS active_haken_saki,
    (SELECT COUNT(*) FROM visa_applications WHERE application_status IN ('draft', 'submitted', 'under_review')) AS pending_applications;

-- ============================================================
-- FUNCIONES
-- ============================================================

-- Función: Generar código de empleado
CREATE OR REPLACE FUNCTION generate_employee_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.employee_code IS NULL OR NEW.employee_code = '' THEN
        NEW.employee_code := 'UNS-' || TO_CHAR(CURRENT_DATE, 'YYYYMM') || '-' || 
                            LPAD(NEXTVAL('employees_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para generar código de empleado
DROP TRIGGER IF EXISTS trg_generate_employee_code ON employees;
CREATE TRIGGER trg_generate_employee_code
    BEFORE INSERT ON employees
    FOR EACH ROW
    EXECUTE FUNCTION generate_employee_code();

-- Función: Actualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER trg_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_haken_moto_updated_at BEFORE UPDATE ON haken_moto_company FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_haken_saki_updated_at BEFORE UPDATE ON haken_saki_company FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_contracts_updated_at BEFORE UPDATE ON employment_contracts FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_dispatch_updated_at BEFORE UPDATE ON dispatch_assignments FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_visa_apps_updated_at BEFORE UPDATE ON visa_applications FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Función: Crear notificación de visa por vencer
CREATE OR REPLACE FUNCTION create_visa_expiration_notifications()
RETURNS void AS $$
DECLARE
    emp RECORD;
BEGIN
    -- Eliminar notificaciones antiguas no leídas
    DELETE FROM notifications 
    WHERE notification_type = 'visa_expiring' 
    AND is_read = FALSE 
    AND created_at < CURRENT_DATE - INTERVAL '7 days';
    
    -- Crear notificaciones para visas que vencen en 90, 60, 30 días
    FOR emp IN 
        SELECT id, employee_code, family_name, given_name, current_expiration_date,
               (current_expiration_date - CURRENT_DATE) AS days_remaining
        FROM employees
        WHERE employment_status = 'active'
        AND current_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
    LOOP
        -- Verificar si ya existe notificación reciente
        IF NOT EXISTS (
            SELECT 1 FROM notifications 
            WHERE employee_id = emp.id 
            AND notification_type = 'visa_expiring'
            AND created_at > CURRENT_DATE - INTERVAL '7 days'
        ) THEN
            INSERT INTO notifications (
                employee_id, notification_type, title, message, due_date, days_before_due
            ) VALUES (
                emp.id,
                'visa_expiring',
                '在留期限通知: ' || emp.family_name || ' ' || emp.given_name,
                '在留期限まで' || emp.days_remaining || '日です。更新手続きを開始してください。',
                emp.current_expiration_date,
                emp.days_remaining
            );
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- DATOS INICIALES
-- ============================================================

-- Insertar tu empresa (UNS) como???
INSERT INTO haken_moto_company (
    company_name, company_name_kana, corporation_number,
    employment_insurance_number, worker_dispatch_license,
    postal_code, prefecture, city, address_line1, full_address,
    telephone, email, representative_name, business_type_name
) VALUES (
    'UNS????', '??????', '1234567890123',
    '12345678901', '?23-300000',
    '486-0000', '???', '????', '???1-1', '??????????1-1',
    '0568-00-0000', 'info@uns.co.jp', '?? ??', '?????'
) ON CONFLICT (corporation_number) DO NOTHING;

-- Insertar usuarios por defecto
-- Admin: admin / admin123
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin', 
    'admin@uns-visa.jp', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO9G', 
    'System Administrator', 
    'admin', 
    true
) ON CONFLICT (username) DO NOTHING;

-- Staff: staff / staff123
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'staff', 
    'staff@uns-visa.jp', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 
    'Staff User', 
    'staff', 
    true
) ON CONFLICT (username) DO NOTHING;

-- ============================================================
-- COMENTARIOS
-- ============================================================

COMMENT ON TABLE employees IS '外国人従業員マスタ - ビザ申請に必要な全情報を保持';
COMMENT ON TABLE haken_moto_company IS '派遣元会社（自社UNS）情報';
COMMENT ON TABLE haken_saki_company IS '派遣先会社（クライアント・工場）情報';
COMMENT ON TABLE employment_contracts IS '雇用契約情報 - 派遣元との契約';
COMMENT ON TABLE dispatch_assignments IS '派遣契約情報 - 派遣先への配属';
COMMENT ON TABLE visa_applications IS 'ビザ申請履歴 - 認定・変更・更新の全記録';
COMMENT ON TABLE employee_family IS '従業員の在日親族情報';
COMMENT ON TABLE employee_work_history IS '従業員の職歴';
COMMENT ON TABLE notifications IS '通知・リマインダー（ビザ期限等）';
COMMENT ON TABLE audit_log IS '監査ログ - データ変更履歴';

COMMENT ON VIEW v_employees_visa_expiring IS '在留期限が近い従業員一覧';
COMMENT ON VIEW v_employees_by_haken_saki IS '派遣先別の従業員数';
COMMENT ON VIEW v_visa_form_data IS 'ビザ申請書に必要な全データ';
COMMENT ON VIEW v_dashboard_stats IS 'ダッシュボード用統計';

-- ============================================================
-- 完了メッセージ
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ UNS Visa System Database initialized successfully!';
    RAISE NOTICE '📊 Tables created: 12';
    RAISE NOTICE '👁️ Views created: 4';
    RAISE NOTICE '🔧 Functions created: 3';
    RAISE NOTICE '🏢 Default company (UNS) inserted';
END $$;
