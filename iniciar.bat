@echo off
:: ╔══════════════════════════════════════════════════════╗
:: ║   LYCAON SOFTWARE — Script de Inicio Rápido (Windows)  ║
:: ║   Doble clic para arrancar el servidor Flask         ║
:: ╚══════════════════════════════════════════════════════╝

echo.
echo  Iniciando Lycaon Software...
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python no está instalado o no está en el PATH.
    echo  Descárgalo desde https://python.org
    pause
    exit /b
)

:: Instalar dependencias si no están instaladas
echo  Verificando dependencias...
pip install -r requirements.txt -q

echo.
echo  Abriendo http://localhost:5000 en el navegador...
start http://localhost:5000

:: Ejecutar el servidor Flask
python app.py

pause
