@echo off
REM Start Card Inventory App with HTTP
REM This batch file starts the FastAPI app without SSL

echo 🌐 Starting Card Inventory App with HTTP...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run: py -m venv .venv
    echo Then run: .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

REM Get IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :found_ip
)
:found_ip
set IP=%IP: =%

echo 📱 Access from iPhone:
echo HTTP: http://192.168.1.26:8000
echo.
echo 💻 Access from computer: http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

REM Start the HTTP server
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
