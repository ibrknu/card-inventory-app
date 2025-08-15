@echo off
REM Start Card Inventory App with HTTPS
REM This batch file starts the FastAPI app with SSL certificates

echo 🔒 Starting Card Inventory App with HTTPS...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run: py -m venv .venv
    echo Then run: .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if SSL certificates exist
if not exist "ssl\cert.pem" (
    echo ❌ SSL certificates not found!
    echo Generating SSL certificates...
    .venv\Scripts\python.exe generate_ssl.py
    if errorlevel 1 (
        echo Failed to generate SSL certificates!
        pause
        exit /b 1
    )
)

REM Get IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
set IP=%IP: =%

echo 📱 Access from iPhone:
echo HTTPS: https://192.168.1.26:8443
echo HTTP:  http://192.168.1.26:8000
echo.
echo 💻 Access from computer: https://localhost:8443
echo ⚠️  Note: You'll see a security warning - click 'Advanced' → 'Proceed'
echo.
echo Press Ctrl+C to stop
echo.

REM Start the HTTPS server
.venv\Scripts\python.exe run_https.py

pause
