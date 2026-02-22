# ============================================================
#  MineVision Dashboard – Setup para PowerShell
#  Uso: .\setup.ps1
#  Si da error de permisos: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# ============================================================

$VENV = ".venv"
$APP  = "app.py"

Write-Host ""
Write-Host "  MineVision Dashboard - Setup" -ForegroundColor Cyan
Write-Host "  ==============================" -ForegroundColor Cyan

# ── Verificar Python ─────────────────────────────────────────
try {
    $pyver = python --version 2>&1
    Write-Host "  Python encontrado: $pyver" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python no encontrado." -ForegroundColor Red
    Write-Host "  Descarga Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# ── Crear entorno virtual ────────────────────────────────────
if (-not (Test-Path "$VENV\Scripts\Activate.ps1")) {
    Write-Host ""
    Write-Host "  Creando entorno virtual en $VENV\ ..." -ForegroundColor Yellow
    python -m venv $VENV
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] No se pudo crear el entorno virtual." -ForegroundColor Red
        exit 1
    }
    Write-Host "  OK  Entorno virtual creado." -ForegroundColor Green
} else {
    Write-Host "  OK  Entorno virtual ya existe." -ForegroundColor Green
}

# ── Activar entorno ──────────────────────────────────────────
Write-Host ""
Write-Host "  Activando entorno virtual ..." -ForegroundColor Yellow
& "$VENV\Scripts\Activate.ps1"

# ── Instalar dependencias ─────────────────────────────────────
Write-Host "  Actualizando pip ..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

Write-Host "  Instalando dependencias ..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Fallo la instalacion de dependencias." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "   Setup completado exitosamente." -ForegroundColor Green
Write-Host "   Ejecuta la app con:" -ForegroundColor White
Write-Host "     .\run.ps1" -ForegroundColor Yellow
Write-Host "     o: python app.py" -ForegroundColor Yellow
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host ""
