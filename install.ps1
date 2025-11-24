# ============================================================
# UNS VISA MANAGEMENT SYSTEM
# Installation Script for Windows (PowerShell)
# ============================================================
# 
# USO:
#   1. Abrir PowerShell como Administrador
#   2. Ejecutar: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   3. Ejecutar: .\install.ps1
#
# ============================================================

param(
    [switch]$SkipDocker,
    [switch]$DevMode,
    [switch]$Help
)

# Colores
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Cyan = "Cyan"

function Write-Step {
    param([string]$Message)
    Write-Host "`n[$([char]0x2714)] " -ForegroundColor $Green -NoNewline
    Write-Host $Message -ForegroundColor $Cyan
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "`n[$([char]0x2718)] " -ForegroundColor $Red -NoNewline
    Write-Host $Message -ForegroundColor $Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "`n[!] " -ForegroundColor $Yellow -NoNewline
    Write-Host $Message -ForegroundColor $Yellow
}

function Show-Banner {
    Clear-Host
    Write-Host @"

    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   🇯🇵  UNS VISA MANAGEMENT SYSTEM                            ║
    ║       派遣会社向けビザ管理システム                           ║
    ║                                                              ║
    ║   Installation Script v1.0                                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
}

function Show-Help {
    Write-Host @"
    
    USO: .\install.ps1 [opciones]

    OPCIONES:
        -SkipDocker     Omitir verificación de Docker (si ya está instalado)
        -DevMode        Modo desarrollo (con hot reload)
        -Help           Mostrar esta ayuda

    EJEMPLOS:
        .\install.ps1                   # Instalación normal
        .\install.ps1 -DevMode          # Modo desarrollo
        .\install.ps1 -SkipDocker       # Omitir verificación de Docker

    REQUISITOS:
        - Windows 10/11
        - Docker Desktop
        - PowerShell 5.1+

    PUERTOS UTILIZADOS:
        - 5433  : PostgreSQL
        - 8100  : API Backend
        - 8180  : Frontend (HTTP)
        - 8143  : Frontend (HTTPS)
        - 6380  : Redis
        - 8181  : Adminer (DB Admin)

"@ -ForegroundColor White
    exit 0
}

function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-DockerInstalled {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Host "  Docker encontrado: $dockerVersion" -ForegroundColor Gray
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Test-DockerRunning {
    try {
        docker info 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Test-PortAvailable {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -eq $connection
}

function Install-Docker {
    Write-Warning-Custom "Docker no está instalado. Descargando Docker Desktop..."
    
    $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    $installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
    
    try {
        Write-Host "  Descargando Docker Desktop..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Host "  Ejecutando instalador..." -ForegroundColor Gray
        Start-Process -FilePath $installerPath -Wait -ArgumentList "install --quiet"
        
        Write-Host "  Docker Desktop instalado. Por favor reinicie su computadora." -ForegroundColor Green
        Write-Host "  Después de reiniciar, ejecute este script nuevamente." -ForegroundColor Yellow
        
        Remove-Item $installerPath -Force
        exit 0
    } catch {
        Write-Error-Custom "Error al instalar Docker: $_"
        Write-Host "  Por favor instale Docker Desktop manualmente desde:" -ForegroundColor Yellow
        Write-Host "  https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
        exit 1
    }
}

function New-EnvFile {
    Write-Step "Creando archivo .env..."
    
    if (Test-Path ".env") {
        Write-Host "  Archivo .env ya existe, creando backup..." -ForegroundColor Gray
        Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    }
    
    # Generar clave secreta aleatoria
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    
    $envContent = @"
# ============================================================
# UNS VISA MANAGEMENT SYSTEM
# Environment Variables
# Generado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# ============================================================

# DATABASE
DB_PASSWORD=unsvisapassword2024
DB_HOST=localhost
DB_PORT=5433
DB_NAME=uns_visa
DB_USER=postgres
DATABASE_URL=postgresql://postgres:unsvisapassword2024@db:5432/uns_visa

# API
SECRET_KEY=$secretKey
DEBUG=$($DevMode.ToString().ToLower())
API_HOST=0.0.0.0
API_PORT=8100

# REDIS
REDIS_HOST=localhost
REDIS_PORT=6380

# COMPANY INFO
COMPANY_NAME=株式会社UNS
COMPANY_CORP_NUMBER=1234567890123
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  Archivo .env creado exitosamente" -ForegroundColor Gray
}

function Test-Ports {
    Write-Step "Verificando puertos disponibles..."
    
    $ports = @(5433, 8100, 8180, 8143, 6380, 8181)
    $portsInUse = @()
    
    foreach ($port in $ports) {
        if (-not (Test-PortAvailable -Port $port)) {
            $portsInUse += $port
        }
    }
    
    if ($portsInUse.Count -gt 0) {
        Write-Warning-Custom "Los siguientes puertos están en uso: $($portsInUse -join ', ')"
        Write-Host "  Por favor cierre las aplicaciones que usan estos puertos o modifique docker-compose.yml" -ForegroundColor Yellow
        
        $continue = Read-Host "  ¿Desea continuar de todos modos? (s/n)"
        if ($continue -ne "s" -and $continue -ne "S") {
            exit 1
        }
    } else {
        Write-Host "  Todos los puertos están disponibles" -ForegroundColor Gray
    }
}

function Start-Services {
    Write-Step "Iniciando servicios con Docker Compose..."
    
    try {
        if ($DevMode) {
            Write-Host "  Modo desarrollo activado (hot reload)" -ForegroundColor Yellow
            docker-compose up -d --build
        } else {
            docker-compose up -d --build
        }
        
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose falló con código $LASTEXITCODE"
        }
        
        Write-Host "  Servicios iniciados correctamente" -ForegroundColor Gray
    } catch {
        Write-Error-Custom "Error al iniciar servicios: $_"
        Write-Host "  Ejecute 'docker-compose logs' para ver los errores" -ForegroundColor Yellow
        exit 1
    }
}

function Wait-ForServices {
    Write-Step "Esperando que los servicios estén listos..."
    
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        $attempt++
        Write-Host "`r  Intento $attempt de $maxAttempts..." -NoNewline -ForegroundColor Gray
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8100/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "`r  API está lista!                    " -ForegroundColor Green
                return $true
            }
        } catch {
            # Continuar esperando
        }
        
        Start-Sleep -Seconds 2
    }
    
    Write-Warning-Custom "Los servicios tardaron más de lo esperado en iniciar"
    Write-Host "  Verifique los logs con: docker-compose logs" -ForegroundColor Yellow
    return $false
}

function Show-Summary {
    Write-Host @"

    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ✅ INSTALACIÓN COMPLETADA                                  ║
    ║                                                              ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║   🌐 URLS DE ACCESO:                                         ║
    ║                                                              ║
    ║      Frontend:     http://localhost:8180                     ║
    ║      API Docs:     http://localhost:8100/docs                ║
    ║      DB Admin:     http://localhost:8181                     ║
    ║                                                              ║
    ║   🗄️ BASE DE DATOS:                                          ║
    ║                                                              ║
    ║      Host:         localhost                                 ║
    ║      Puerto:       5433                                      ║
    ║      Database:     uns_visa                                  ║
    ║      Usuario:      postgres                                  ║
    ║      Password:     (ver archivo .env)                        ║
    ║                                                              ║
    ║   📋 COMANDOS ÚTILES:                                        ║
    ║                                                              ║
    ║      Ver logs:     docker-compose logs -f                    ║
    ║      Detener:      docker-compose down                       ║
    ║      Reiniciar:    docker-compose restart                    ║
    ║      Estado:       docker-compose ps                         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

    # Abrir navegador
    $openBrowser = Read-Host "¿Desea abrir el navegador? (s/n)"
    if ($openBrowser -eq "s" -or $openBrowser -eq "S") {
        Start-Process "http://localhost:8180"
    }
}

function New-Shortcuts {
    Write-Step "Creando accesos directos..."
    
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $projectPath = (Get-Location).Path
    
    # Crear script de inicio rápido
    $startScript = @"
@echo off
cd /d "$projectPath"
docker-compose up -d
start http://localhost:8180
"@
    $startScript | Out-File -FilePath "$desktopPath\UNS Visa - Iniciar.bat" -Encoding ASCII
    
    # Crear script de detener
    $stopScript = @"
@echo off
cd /d "$projectPath"
docker-compose down
"@
    $stopScript | Out-File -FilePath "$desktopPath\UNS Visa - Detener.bat" -Encoding ASCII
    
    Write-Host "  Accesos directos creados en el escritorio" -ForegroundColor Gray
}

# ============================================================
# MAIN
# ============================================================

if ($Help) {
    Show-Help
}

Show-Banner

# Verificar si es administrador (solo advertencia)
if (-not (Test-Administrator)) {
    Write-Warning-Custom "Se recomienda ejecutar como Administrador para mejor compatibilidad"
}

# Verificar Docker
if (-not $SkipDocker) {
    Write-Step "Verificando Docker..."
    
    if (-not (Test-DockerInstalled)) {
        Install-Docker
    }
    
    if (-not (Test-DockerRunning)) {
        Write-Warning-Custom "Docker Desktop no está ejecutándose"
        Write-Host "  Iniciando Docker Desktop..." -ForegroundColor Gray
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        
        Write-Host "  Esperando que Docker inicie (puede tomar 1-2 minutos)..." -ForegroundColor Gray
        $dockerStarted = $false
        for ($i = 0; $i -lt 60; $i++) {
            Start-Sleep -Seconds 2
            if (Test-DockerRunning) {
                $dockerStarted = $true
                break
            }
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
        
        if (-not $dockerStarted) {
            Write-Error-Custom "Docker no pudo iniciar. Por favor inícielo manualmente y ejecute este script nuevamente."
            exit 1
        }
        Write-Host ""
    }
    
    Write-Host "  Docker está ejecutándose" -ForegroundColor Gray
}

# Verificar puertos
Test-Ports

# Crear archivo .env
New-EnvFile

# Iniciar servicios
Start-Services

# Esperar que los servicios estén listos
Wait-ForServices

# Crear accesos directos
New-Shortcuts

# Mostrar resumen
Show-Summary

Write-Host "`n¡Instalación completada! 🎉`n" -ForegroundColor Green
