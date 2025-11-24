# 🇯🇵 UNS Visa Management System

Sistema completo de gestión de visas y compañías派遣 con backend FastAPI/PostgreSQL y frontend estático en Tailwind.

## 📦 Visión general del repositorio
- **Backend (FastAPI)**: `backend/` expone routers de autenticación, validadores y CRUD en memoria para **派遣先 (Haken Saki)**. El pool `asyncpg` está preparado para PostgreSQL en `main.py`.
- **Base de datos**: `database/init.sql` define un esquema amplio para empleados, contratos, asignaciones y empresas tanto **派遣元** como **派遣先**.
- **Frontend estático**: páginas HTML en `frontend/` consumen la API directamente (sin build tools). Se incluye navegación, dashboards y modales de edición con Tailwind.
- **Contenedores**: `docker-compose.yml` levanta API, base de datos y frontend estático.

### Tablas clave analizadas (database/init.sql)
- **employees** (`従業員`): almacena datos personales, contacto en Japón, pasaporte/visa, historial y estado laboral. Incluye campos como `family_name`, `nationality`, `current_visa_status`, `residence_card_number`, fechas de expiración y metadatos de auditoría.【F:database/init.sql†L46-L136】【F:database/init.sql†L200-L234】
- **haken_saki_company** (`派遣先会社`): datos de clientes/fábricas: nombre y sucursal, números oficiales (`corporation_number`, `employment_insurance_number`), dirección completa, contacto (`telephone`, `contact_person`, `contact_email`), indicadores de negocio y contrato, empleados totales y notas.【F:database/init.sql†L21-L91】
- **dispatch_assignments / employment_contracts**: vinculan empleados con派遣元/先 y controlan periodos, puestos y estado del contrato.【F:database/init.sql†L235-L296】

## 🚀 Puesta en marcha rápida
```bash
# 1) Clonar y situarte en el proyecto
cd Saca-visitas-V1.0-11.25

# 2) Arrancar servicios
docker compose up -d

# 3) URLs por defecto
# API docs:      http://localhost:8100/docs
# Frontend:      http://localhost:8180
# Adminer (DB):  http://localhost:8181
```

## 🧭 Frontend disponible
- `frontend/index.html`: dashboard con accesos rápidos y estadísticas.
- `frontend/employees.html`: gestor de empleados con filtros, exportación y modal de alta/edición.
- `frontend/import.html`: importación de empleados (Excel) y派遣先 (JSON).
- `frontend/haken-saki.html`: **nuevo editor de派遣先** para revisar y completar información faltante.

## 🏭 Editor de Haken Saki
La nueva página `frontend/haken-saki.html` permite:
- Listar派遣先 activos, buscar por nombre/dirección y ver tags de **“Información incompleta”** cuando faltan campos críticos.
- Abrir un modal para crear o completar datos (números oficiales, dirección, contacto, contrato, indicadores de negocio) y enviarlos a la API `/api/haken-saki` (POST/PUT).
- Marcar compañías como inactivas o eliminarlas con el endpoint DELETE `/api/haken-saki/{id}`.

## 🔌 API relevante
- `GET /api/haken-saki`: listado con soporte de búsqueda y filtro de activos.
- `POST /api/haken-saki`: alta de派遣先 con validaciones básicas.
- `PUT /api/haken-saki/{id}`: actualización parcial.
- `DELETE /api/haken-saki/{id}?hard_delete=false`: baja lógica (por defecto) o eliminación.

## 🧪 Tests
No se incluyen suites automatizadas; se recomienda probar manualmente los flujos principales (listado, creación, edición y desactivación de派遣先) desde el frontend nuevo.
