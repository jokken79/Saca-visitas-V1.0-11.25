@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: ============================================================
:: UNS VISA MANAGEMENT SYSTEM
:: Installation Script for Windows (Batch)
:: ============================================================
::
:: USO: Doble clic en install.bat o ejecutar desde CMD
::
:: ============================================================

title UNS Visa System - Instalación

:: Colores (usando PowerShell para colores)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "RESET=[0m"

:: Banner
cls
echo.
echo %CYAN%╔══════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║                                                              ║%RESET%
echo %CYAN%║   🇯🇵  UNS VISA MANAGEMENT SYSTEM                            ║%RESET%
echo %CYAN%║       派遣会社向けビザ管理システム                           ║%RESET%
echo %CYAN%║                                                              ║%RESET%
echo %CYAN%║   Installation Script v1.0                                   ║%RESET%
echo %CYAN%║                                                              ║%RESET%
echo %CYAN%╚══════════════════════════════════════════════════════════════╝%RESET%
echo.

:: ============================================================
:: PASO 1: Verificar Docker
:: ============================================================
echo %GREEN%[1/6]%RESET% Verificando Docker...

docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[X] Docker no está instalado%RESET%
    echo.
    echo     Por favor instale Docker Desktop desde:
    echo     %CYAN%https://www.docker.com/products/docker-desktop%RESET%
    echo.
    echo     Después de instalar, reinicie su PC y ejecute este script nuevamente.
    echo.
    pause
    exit /b 1
)

docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%[!] Docker Desktop no está ejecutándose%RESET%
    echo     Iniciando Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo     Esperando que Docker inicie (puede tomar 1-2 minutos)...
    :WAIT_DOCKER
    timeout /t 5 /nobreak >nul
    docker info >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo     Aún esperando...
        goto WAIT_DOCKER
    )
)

echo     %GREEN%Docker está ejecutándose%RESET%

:: ============================================================
:: PASO 2: Verificar puertos
:: ============================================================
echo.
echo %GREEN%[2/6]%RESET% Verificando puertos disponibles...

set PORTS_OK=1

netstat -an | findstr ":5433 " >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     %YELLOW%[!] Puerto 5433 está en uso (PostgreSQL)%RESET%
    set PORTS_OK=0
)

netstat -an | findstr ":8100 " >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     %YELLOW%[!] Puerto 8100 está en uso (API)%RESET%
    set PORTS_OK=0
)

netstat -an | findstr ":8180 " >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     %YELLOW%[!] Puerto 8180 está en uso (Frontend)%RESET%
    set PORTS_OK=0
)

netstat -an | findstr ":8181 " >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo     %YELLOW%[!] Puerto 8181 está en uso (Adminer)%RESET%
    set PORTS_OK=0
)

if %PORTS_OK% EQU 0 (
    echo.
    echo     %YELLOW%Algunos puertos están en uso.%RESET%
    echo     Cierre las aplicaciones que usan estos puertos o modifique docker-compose.yml
    echo.
    set /p CONTINUE="¿Desea continuar de todos modos? (s/n): "
    if /i not "!CONTINUE!"=="s" (
        echo     Instalación cancelada.
        pause
        exit /b 1
    )
) else (
    echo     %GREEN%Todos los puertos están disponibles%RESET%
)

:: ============================================================
:: PASO 3: Crear archivo .env
:: ============================================================
echo.
echo %GREEN%[3/6]%RESET% Creando archivo de configuración...

if exist .env (
    echo     Archivo .env ya existe, creando backup...
    copy .env .env.backup >nul
)

:: Generar clave secreta (simple)
set CHARS=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
set SECRET_KEY=
for /L %%i in (1,1,32) do (
    set /a RAND=!random! %% 62
    for %%j in (!RAND!) do set SECRET_KEY=!SECRET_KEY!!CHARS:~%%j,1!
)

:: Escribir .env
(
echo # ============================================================
echo # UNS VISA MANAGEMENT SYSTEM
echo # Environment Variables
echo # Generado: %date% %time%
echo # ============================================================
echo.
echo # DATABASE
echo DB_PASSWORD=unsvisapassword2024
echo DB_HOST=localhost
echo DB_PORT=5433
echo DB_NAME=uns_visa
echo DB_USER=postgres
echo DATABASE_URL=postgresql://postgres:unsvisapassword2024@db:5432/uns_visa
echo.
echo # API
echo SECRET_KEY=!SECRET_KEY!
echo DEBUG=false
echo API_HOST=0.0.0.0
echo API_PORT=8100
echo.
echo # REDIS
echo REDIS_HOST=localhost
echo REDIS_PORT=6380
echo.
echo # COMPANY INFO
echo COMPANY_NAME=株式会社UNS
echo COMPANY_CORP_NUMBER=1234567890123
) > .env

echo     %GREEN%Archivo .env creado%RESET%

:: ============================================================
:: PASO 4: Crear directorios necesarios
:: ============================================================
echo.
echo %GREEN%[4/6]%RESET% Creando directorios...

if not exist "uploads" mkdir uploads
if not exist "generated" mkdir generated
if not exist "nginx\ssl" mkdir nginx\ssl

echo     %GREEN%Directorios creados%RESET%

:: ============================================================
:: PASO 5: Iniciar Docker Compose
:: ============================================================
echo.
echo %GREEN%[5/6]%RESET% Iniciando servicios con Docker...
echo     Esto puede tomar varios minutos la primera vez...
echo.

docker-compose up -d --build

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo %RED%[X] Error al iniciar los servicios%RESET%
    echo     Ejecute 'docker-compose logs' para ver los errores
    pause
    exit /b 1
)

:: ============================================================
:: PASO 6: Esperar que los servicios estén listos
:: ============================================================
echo.
echo %GREEN%[6/6]%RESET% Esperando que los servicios estén listos...

set ATTEMPTS=0
set MAX_ATTEMPTS=30

:CHECK_HEALTH
set /a ATTEMPTS+=1
if %ATTEMPTS% GTR %MAX_ATTEMPTS% (
    echo.
    echo %YELLOW%[!] Los servicios tardaron más de lo esperado%RESET%
    echo     Verifique los logs con: docker-compose logs
    goto SUMMARY
)

timeout /t 2 /nobreak >nul

curl -s http://localhost:8100/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo     Intento %ATTEMPTS% de %MAX_ATTEMPTS%...
    goto CHECK_HEALTH
)

echo     %GREEN%¡Servicios listos!%RESET%

:: ============================================================
:: CREAR ACCESOS DIRECTOS
:: ============================================================
echo.
echo Creando accesos directos en el escritorio...

set DESKTOP=%USERPROFILE%\Desktop
set PROJECT_PATH=%CD%

:: Script para iniciar
(
echo @echo off
echo cd /d "%PROJECT_PATH%"
echo docker-compose up -d
echo start http://localhost:8180
echo timeout /t 3
) > "%DESKTOP%\UNS Visa - Iniciar.bat"

:: Script para detener
(
echo @echo off
echo cd /d "%PROJECT_PATH%"
echo docker-compose down
echo pause
) > "%DESKTOP%\UNS Visa - Detener.bat"

:: Script para ver logs
(
echo @echo off
echo cd /d "%PROJECT_PATH%"
echo docker-compose logs -f
) > "%DESKTOP%\UNS Visa - Ver Logs.bat"

echo     %GREEN%Accesos directos creados%RESET%

:: ============================================================
:: RESUMEN
:: ============================================================
:SUMMARY
echo.
echo.
echo %GREEN%╔══════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%║   ✅ INSTALACIÓN COMPLETADA                                  ║%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%╠══════════════════════════════════════════════════════════════╣%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%║   🌐 URLS DE ACCESO:                                         ║%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%║      Frontend:     http://localhost:8180                     ║%RESET%
echo %GREEN%║      API Docs:     http://localhost:8100/docs                ║%RESET%
echo %GREEN%║      DB Admin:     http://localhost:8181                     ║%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%║   🗄️ BASE DE DATOS:                                          ║%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%║      Host:         localhost                                 ║%RESET%
echo %GREEN%║      Puerto:       5433                                      ║%RESET%
echo %GREEN%║      Database:     uns_visa                                  ║%RESET%
echo %GREEN%║      Usuario:      postgres                                  ║%RESET%
echo %GREEN%║      Password:     unsvisapassword2024                       ║%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%║   📋 COMANDOS ÚTILES:                                        ║%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%║      Ver logs:     docker-compose logs -f                    ║%RESET%
echo %GREEN%║      Detener:      docker-compose down                       ║%RESET%
echo %GREEN%║      Reiniciar:    docker-compose restart                    ║%RESET%
echo %GREEN%║      Estado:       docker-compose ps                         ║%RESET%
echo %GREEN%║                                                              ║%RESET%
echo %GREEN%╚══════════════════════════════════════════════════════════════╝%RESET%
echo.

set /p OPEN_BROWSER="¿Desea abrir el navegador? (s/n): "
if /i "%OPEN_BROWSER%"=="s" (
    start http://localhost:8180
)

echo.
echo %GREEN%¡Instalación completada! 🎉%RESET%
echo.
pause
