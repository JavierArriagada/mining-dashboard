@echo off
:: ============================================================
::  MineVision Dashboard – Ejecutar App
:: ============================================================

setlocal
set VENV=.venv

if not exist "%VENV%\Scripts\activate.bat" (
    echo  [ERROR] Entorno virtual no encontrado.
    echo  Ejecuta primero: setup.bat
    pause
    exit /b 1
)

echo.
echo  Activando entorno virtual ...
call %VENV%\Scripts\activate.bat

echo  Iniciando MineVision Dashboard ...
echo  Abre tu navegador en:  http://localhost:8050
echo  Presiona Ctrl+C para detener.
echo.
python app.py

endlocal
