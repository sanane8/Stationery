@echo off
echo Setting up Stationery Tracker Django Application
echo ================================================

echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo Python is not available. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements. Please check your internet connection.
    pause
    exit /b 1
)

echo Creating migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo Failed to create migrations.
    pause
    exit /b 1
)

echo Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Failed to run migrations.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Create a superuser: python manage.py createsuperuser
echo 2. Run the server: python manage.py runserver
echo 3. Open http://127.0.0.1:8000/ in your browser
echo 4. Access admin panel at http://127.0.0.1:8000/admin/
echo.
echo For detailed instructions, see README.md
pause
