g@echo off
REM Setup script for Flame CLI on Windows

echo.
echo ======================================
echo 🔥 Flame CLI Setup Script
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

REM Create virtual environment
if not exist venv (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

REM Install dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

REM Setup .env file
echo.
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo ✅ .env created - Please edit it with your API key
) else (
    echo ✅ .env already exists
)

REM Test setup
echo.
echo Testing setup...
python main.py --version
if errorlevel 1 (
    echo ❌ Setup test failed
    pause
    exit /b 1
)
echo ✅ Setup test passed

REM Final instructions
echo.
echo ======================================
echo ✅ Setup Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Edit .env file and add your HACK_CLUB_API_KEY
echo 2. Run: python main.py --check
echo 3. Run: python main.py
echo.
echo For more help, see README.md or QUICKSTART.md
echo.
pause

