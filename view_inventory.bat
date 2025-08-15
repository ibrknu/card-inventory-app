@echo off
REM View Card Inventory
REM This batch file displays all items in your card inventory

echo 📊 Viewing Card Inventory...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found!
    echo Please run the app first to set up the environment.
    pause
    exit /b 1
)

REM Check if database exists
if not exist "card_inventory.db" (
    echo ❌ Database not found!
    echo Please run the app first to create the database.
    pause
    exit /b 1
)

REM Check if search term provided
if "%1"=="" (
    echo Viewing all items...
    .venv\Scripts\python.exe view_inventory.py
) else (
    echo Searching for: %1
    .venv\Scripts\python.exe view_inventory.py "%1"
)

echo.
echo Press any key to continue...
pause >nul
