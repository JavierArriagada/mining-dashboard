# ============================================================
#  MineVision Dashboard – Ejecutar App (PowerShell)
# ============================================================

$VENV = ".venv"

if (-not (Test-Path "$VENV\Scripts\Activate.ps1")) {
    Write-Host "  [ERROR] Entorno virtual no encontrado." -ForegroundColor Red
    Write-Host "  Ejecuta primero: .\setup.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "  Activando entorno virtual ..." -ForegroundColor Yellow
& "$VENV\Scripts\Activate.ps1"

Write-Host "  Iniciando MineVision Dashboard ..." -ForegroundColor Cyan
Write-Host "  Abre tu navegador en: http://localhost:8050" -ForegroundColor Green
Write-Host "  Presiona Ctrl+C para detener." -ForegroundColor White
Write-Host ""

python app.py
