@echo off
REM Stationery Management System - Windows Deployment Script
REM Tanzania Local Production Setup

echo.
echo ========================================
echo   Stationery Management System Setup
echo   Windows Production Deployment
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Please run this script as Administrator
    echo Right-click the file and select "Run as administrator"
    pause
    exit /b 1
)

REM Create project directory
echo 📁 Creating project directory...
if not exist "C:\stationery" mkdir "C:\stationery"
if not exist "C:\stationery\logs" mkdir "C:\stationery\logs"
if not exist "C:\stationery\backups" mkdir "C:\stationery\backups"
if not exist "C:\stationery\media" mkdir "C:\stationery\media"
if not exist "C:\stationery\staticfiles" mkdir "C:\stationery\staticfiles"

REM Copy project files
echo 📋 Copying project files...
xcopy /E /I /Y "%~dp0*" "C:\stationery\"

REM Change to project directory
cd /d C:\stationery

REM Check Python installation
echo 🐍 Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Create virtual environment
echo 🐍 Creating virtual environment...
if exist "venv" rmdir /s /q venv
python -m venv venv

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing production requirements...
pip install -r requirements_production.txt

REM Install PostgreSQL (check if installed)
echo 🗄️ Checking PostgreSQL installation...
psql --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️ PostgreSQL not found. Please install PostgreSQL from:
    echo https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
    echo.
    echo After installation:
    echo 1. Set password for postgres user (recommended: postgres2024)
    echo 2. Install pgAdmin 4 (optional)
    echo 3. Continue this script
    echo.
    pause
)

REM Create database setup script
echo 🗄️ Creating database setup script...
(
echo CREATE DATABASE stationery_db;
echo CREATE USER stationery_user WITH PASSWORD 'stationery2024';
echo GRANT ALL PRIVILEGES ON DATABASE stationery_db TO stationery_user;
echo ALTER USER stationery_user CREATEDB;
echo \q
) > create_db.sql

REM Instructions for database setup
echo.
echo 🗄️ Database Setup Instructions:
echo 1. Open pgAdmin or Command Prompt
echo 2. Connect to PostgreSQL with postgres user
echo 3. Run the commands from create_db.sql file
echo 4. Press any key when database is created...
pause >nul

REM Create production settings
echo ⚙️ Creating production settings...
(
echo import os
echo from pathlib import Path
echo.
echo BASE_DIR = Path(__file__).resolve().parent.parent
echo.
echo SECRET_KEY = 'django-insecure-production-key-change-this'
echo DEBUG = False
echo ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100', '0.0.0.0']
echo.
echo INSTALLED_APPS = [
echo     'django.contrib.admin',
echo     'django.contrib.auth',
echo     'django.contrib.contenttypes',
echo     'django.contrib.sessions',
echo     'django.contrib.messages',
echo     'django.contrib.staticfiles',
echo     'tracker',
echo ]
echo.
echo MIDDLEWARE = [
echo     'django.middleware.security.SecurityMiddleware',
echo     'django.contrib.sessions.middleware.SessionMiddleware',
echo     'django.middleware.common.CommonMiddleware',
echo     'django.middleware.csrf.CsrfViewMiddleware',
echo     'django.contrib.auth.middleware.AuthenticationMiddleware',
echo     'django.contrib.messages.middleware.MessageMiddleware',
echo     'django.middleware.clickjacking.XFrameOptionsMiddleware',
echo ]
echo.
echo ROOT_URLCONF = 'stationery_tracker.urls'
echo.
echo TEMPLATES = [
echo     {
echo         'BACKEND': 'django.template.backends.django.DjangoTemplates',
echo         'DIRS': [BASE_DIR / 'templates'],
echo         'APP_DIRS': True,
echo         'OPTIONS': {
echo             'context_processors': [
echo                 'django.template.context_processors.debug',
echo                 'django.template.context_processors.request',
echo                 'django.contrib.auth.context_processors.auth',
echo                 'django.contrib.messages.context_processors.messages',
echo             ],
echo         },
echo     },
echo ]
echo.
echo WSGI_APPLICATION = 'stationery_tracker.wsgi.application'
echo.
echo DATABASES = {
echo     'default': {
echo         'ENGINE': 'django.db.backends.postgresql',
echo         'NAME': 'stationery_db',
echo         'USER': 'stationery_user',
echo         'PASSWORD': 'stationery2024',
echo         'HOST': 'localhost',
echo         'PORT': '5432',
echo     }
echo }
echo.
echo AUTH_PASSWORD_VALIDATORS = [
echo     {
echo         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
echo     },
echo     {
echo         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
echo     },
echo     {
echo         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
echo     },
echo     {
echo         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
echo     },
echo ]
echo.
echo LANGUAGE_CODE = 'en-us'
echo TIME_ZONE = 'Africa/Dar_es_Salaam'
echo USE_I18N = True
echo USE_TZ = True
echo.
echo STATIC_URL = '/static/'
echo STATIC_ROOT = BASE_DIR / 'staticfiles'
echo STATICFILES_DIRS = [BASE_DIR / 'static']
echo MEDIA_URL = '/media/'
echo MEDIA_ROOT = BASE_DIR / 'media'
echo.
echo DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
echo.
echo LOGGING = {
echo     'version': 1,
echo     'disable_existing_loggers': False,
echo     'handlers': {
echo         'file': {
echo             'level': 'INFO',
echo             'class': 'logging.FileHandler',
echo             'filename': BASE_DIR / 'logs' / 'django.log',
echo         },
echo     },
echo     'loggers': {
echo         'django': {
echo             'handlers': ['file'],
echo             'level': 'INFO',
echo             'propagate': True,
echo         },
echo         'tracker': {
echo             'handlers': ['file'],
echo             'level': 'INFO',
echo             'propagate': True,
echo         },
echo     },
echo }
) > stationery_tracker\production_settings.py

REM Run database migrations
echo 🗄️ Running database migrations...
set DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings
python manage.py makemigrations
python manage.py migrate

REM Create superuser
echo 👤 Creating superuser...
python manage.py createsuperuser

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Create Windows service script
echo 🔧 Creating Windows service script...
(
echo @echo off
echo cd /d C:\stationery
echo call venv\Scripts\activate.bat
echo set DJANGO_SETTINGS_MODULE=stationery_tracker.production_settings
echo gunicorn --bind 0.0.0.0:8000 --workers 4 stationery_tracker.wsgi:application
) > start_stationery.bat

REM Create startup script
echo 🔧 Creating startup script...
(
echo @echo off
echo echo Starting Stationery Management System...
echo cd /d C:\stationery
echo call start_stationery.bat
) > start_system.bat

REM Create backup script
echo 💾 Creating backup script...
(
echo @echo off
echo echo Creating backup...
echo cd /d C:\stationery
echo set BACKUP_DIR=C:\stationery\backups
echo set DATE=%date:~-4%_%date:~4,2%_%date:~7,2%
echo.
echo REM Database backup
echo pg_dump -U stationery_user -h localhost stationery_db ^> "%BACKUP_DIR%\stationery_backup_%DATE%.sql"
echo.
echo REM Compress backup
echo powershell -Command "Compress-Archive -Path '%BACKUP_DIR%\stationery_backup_%DATE%.sql' -DestinationPath '%BACKUP_DIR%\stationery_backup_%DATE%.zip' -Force"
echo del "%BACKUP_DIR%\stationery_backup_%DATE%.sql"
echo.
echo REM Media files backup
echo powershell -Command "Compress-Archive -Path 'C:\stationery\media' -DestinationPath '%BACKUP_DIR%\media_backup_%DATE%.zip' -Force"
echo.
echo echo Backup completed: %BACKUP_DIR%\stationery_backup_%DATE%.zip
) > backup.bat

REM Create desktop shortcuts
echo 🖥️ Creating desktop shortcuts...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Stationery System.lnk'); $Shortcut.TargetPath = 'C:\stationery\start_system.bat'; $Shortcut.Save()"

REM Configure Windows Firewall
echo 🔥 Configuring Windows Firewall...
netsh advfirewall firewall add rule name="Stationery HTTP" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="Stationery HTTPS" dir=in action=allow protocol=TCP localport=443

REM Test installation
echo 🧪 Testing installation...
python manage.py check --deploy

echo.
echo ✅ Windows deployment completed successfully!
echo.
echo 📋 Next Steps:
echo 1. Double-click "Stationery System" on desktop to start
echo 2. Open browser and go to: http://localhost:8000
echo 3. Login with superuser credentials
echo 4. Create staff accounts
echo 5. Configure business settings
echo.
echo 📱 Mobile Access:
echo - Connect devices to same WiFi network
echo - Find your computer's IP address (ipconfig)
echo - Access via: http://[YOUR_IP]:8000
echo.
echo 💾 Backup:
echo - Run backup.bat for manual backup
echo - Schedule automatic backup via Task Scheduler
echo.
echo 📞 Support: +255 746 840 409
echo 📧 Email: paul.sanane@gmail.com
echo.
pause
