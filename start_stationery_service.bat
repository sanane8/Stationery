@echo off
REM Stationery Management System - Windows Service Start Script
REM Production Service for Tanzania

title Stationery Management System

echo ========================================
echo   Stationery Management System
echo   Starting Production Service...
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Please run this script as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Change to project directory
cd /d C:\stationery

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found
    echo Please run deploy_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🐍 Activating virtual environment...
call venv\Scripts\activate.bat

REM Set environment variables
set DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings

REM Check if PostgreSQL is running
echo 🗄️ Checking PostgreSQL connection...
pg_isready -h localhost -p 5432 >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️ PostgreSQL is not running
    echo Please start PostgreSQL service
    pause
    exit /b 1
)

REM Run Django checks
echo 🔧 Running Django system checks...
python manage.py check --deploy
if %errorLevel% neq 0 (
    echo ❌ Django system checks failed
    pause
    exit /b 1
)

REM Start Gunicorn server
echo 🚀 Starting Stationery Management System...
echo Access URL: http://localhost:8000
echo Mobile URL: http://[YOUR_IP]:8000
echo Press Ctrl+C to stop the server
echo.

gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 stationery_tracker.wsgi:application

echo.
echo Stationery Management System stopped
pause
