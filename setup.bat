@echo off
:: ============================================================
::  MineVision Dashboard – Setup para Windows CMD / PowerShell
::  Uso: doble-clic o ejecutar desde CMD
:: ============================================================

setlocal
set VENV=.venv
set APP=app.py

echo.
echo  MineVision Dashboard - Setup
echo  ==============================

:: ── Verificar Python ────────────────────────────────────────
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python no encontrado en el PATH.
    echo  Descarga Python desde: https://www.python.org/downloads/
    echo  Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version') do set PYVER=%%v
echo  Python encontrado: %PYVER%

:: ── Crear entorno virtual ────────────────────────────────────
if not exist "%VENV%\Scripts\activate.bat" (
    echo.
    echo  Creando entorno virtual en %VENV%\ ...
    python -m venv %VENV%
    if %errorlevel% neq 0 (
        echo  [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo  OK  Entorno virtual creado.
) else (
    echo  OK  Entorno virtual ya existe.
)

:: ── Activar entorno e instalar dependencias ──────────────────
echo.
echo  Activando entorno virtual ...
call %VENV%\Scripts\activate.bat

echo  Actualizando pip ...
python -m pip install --upgrade pip --quiet

echo  Instalando dependencias ...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo  [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   Setup completado exitosamente.
echo   Ejecuta la app con:  run.bat
echo   o manualmente:       python app.py
echo  ============================================
echo.
pause
endlocal
