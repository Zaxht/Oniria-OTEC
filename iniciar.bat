@echo off
setlocal
cd /d "%~dp0"
title OTEC - Servidor local
if not exist ".venv\Scripts\python.exe" (
    echo No se encontro el entorno virtual .venv. Revisa README.md.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "scripts\iniciar.py" %*
if errorlevel 1 (
    echo.
    echo No se pudo iniciar OTEC. Revisa el mensaje anterior.
    pause
    exit /b 1
)
endlocal
