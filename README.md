# 🇯🇵 UNS Visa Management System

## 派遣会社向けビザ管理システム

Sistema completo de gestión de visas para empresas派遣 (Haken) en Japón.

---

## 🚀 Instalación Rápida

### Windows (Doble clic)
```
install.bat
```

### Windows (PowerShell)
```powershell
.\install.ps1
```

### Después de instalar
| Servicio | URL |
|----------|-----|
| 🌐 Frontend | http://localhost:8180 |
| 📚 API Docs | http://localhost:8100/docs |
| 🗄️ DB Admin | http://localhost:8181 |

**Credenciales de demo:**
- Admin: `admin` / `admin123`
- Staff: `staff` / `staff123`

---

## 📋 Características

### ✅ OCR Automático
- Lectura automática de **在留カード** (Zairyu Card)
- Lectura automática de **パスポート** (Passport)
- Auto-completado de formularios

### ✅ Generación de Excel Oficial
- Formato idéntico al oficial de **出入国在留管理庁**
- 4 hojas: 申請人等作成用１～３, 所属機関等作成用
- Listo para presentar en入管

### ✅ Gestión派遣
- **派遣元** (Haken Moto) - Tu empresa
- **派遣先** (Haken Saki) - Fábricas/clientes
- Relación completa de trabajadores y contratos

### ✅ Validaciones Completas
- 在留カード番号 (AB12345678CD)
- 法人番号 (13 dígitos)
- 雇用保険適用事業所番号 (11 dígitos)
- Teléfonos japoneses
- Código postal

### ✅ Alertas Automáticas
- Visas próximas a vencer (90, 60, 30 días)
- Documentos pendientes
- Renovaciones necesarias

---

## 🛠️ Tecnologías

| Componente | Tecnología |
|------------|------------|
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL 15 |
| Frontend | React + TailwindCSS |
| OCR | Claude AI Vision |
| Excel | openpyxl |
| Container | Docker |

---

## 🚀 Instalación

### Requisitos
- Docker & Docker Compose
- Git

### Pasos

```bash
# 1. Clonar repositorio
git clone https://github.com/your-repo/uns-visa-system.git
cd uns-visa-system

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Iniciar servicios
docker-compose up -d

# 4. Verificar
curl http://localhost:8000/health
```

### URLs

| Servicio | URL |
|----------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Frontend | http://localhost:80 |
| Adminer (DB) | http://localhost:8080 |

---

## 📁 Estructura del Proyecto

```
uns-visa-system/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── excel_generator.py   # Generador de Excel oficial
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── index.html           # Formulario con OCR
│   └── validators.js        # Validaciones en JS
├── database/
│   └── init.sql             # Schema inicial
├── docker-compose.yml
└── README.md
```

---

## 📊 API Endpoints

### Employees (従業員)

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/employees` | Listar empleados |
| POST | `/api/employees` | Crear empleado |
| GET | `/api/employees/{id}` | Obtener por ID |
| GET | `/api/employees/card/{number}` | Buscar por在留カード |

### OCR

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/ocr/import` | Importar datos de OCR |

### Validation (検証)

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/validate/card` | Validar在留カード番号 |
| POST | `/api/validate/corporation` | Validar法人番号 |

### Alerts (アラート)

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/alerts/expiring?days=90` | Visas por vencer |

### Statistics (統計)

| Method | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard stats |

---

## 🗄️ Base de Datos

### Tablas Principales

```sql
-- Empresa派遣元 (tu empresa)
haken_moto_company

-- Empresas派遣先 (fábricas)
haken_saki_company

-- Empleados
employees

-- Contratos de empleo
employment_contracts

-- Asignaciones de派遣
dispatch_assignments

-- Solicitudes de visa
visa_applications
```

### Vista para Formularios
```sql
-- Obtiene todos los datos necesarios para generar申請書
SELECT * FROM v_visa_form_data WHERE employee_id = ?
```

---

## ✅ Validaciones

### 在留カード番号
```
Formato: XX99999999XX
Ejemplo: AB12345678CD
```

### 法人番号
```
Formato: 9999999999999 (13 dígitos)
Incluye validación de checksum
```

### 雇用保険適用事業所番号
```
Formato: 99999999999 (11 dígitos)
Display: 9999-999999-9
```

---

## 📝 Formularios Soportados

1. **在留期間更新許可申請書** (Renewal)
   - Para personas que ya están en Japón
   - Visa próxima a vencer

2. **在留資格認定証明書交付申請書** (COE)
   - Para nuevos empleados en el extranjero
   - Primera entrada a Japón

3. **在留資格変更許可申請書** (Change)
   - Cambio de tipo de visa
   - Ej: 留学 → 技術・人文知識・国際業務

---

## 🔒 Seguridad

- Datos sensibles encriptados
- HTTPS obligatorio en producción
- Validación de entrada en frontend y backend
- Logs de auditoría

---

## 📞 Soporte

Para preguntas o problemas:
- Email: support@uns-visa.jp
- GitHub Issues

---

## 📜 Licencia

MIT License - Uso libre para empresas派遣 en Japón.

---

## 🙏 Créditos

Desarrollado con ❤️ por el equipo de UNS
Powered by Claude AI
