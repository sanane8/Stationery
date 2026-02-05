
# PythonAnywhere Deployment Instructions

## 1. Sign Up for Free Account
- Go to pythonanywhere.com
- Create free account (Bash console + Web app)

## 2. Upload Your Files
- Use the "Files" tab to upload your project
- Or use Git: git clone https://github.com/yourusername/Stationery

## 3. Set Up Virtual Environment
```bash
mkvirtualenv --python=python3.11 stationery
workon stationery
pip install -r requirements_pythonanywhere.txt
```

## 4. Configure Database
- Go to "Databases" tab
- Create PostgreSQL database
- Note connection details

## 5. Set Environment Variables
```bash
export SECRET_KEY='your-secret-key-here'
export DATABASE_URL='your-database-url'
export DEBUG=False
```

## 6. Configure Web App
- Go to "Web" tab
- Create new web app
- Select "Manual configuration"
- Python version: 3.11
- Point to your pythonanywhere_wsgi.py file
- Set virtualenv: /home/yourusername/.virtualenvs/stationery

## 7. Run Migrations
```bash
python manage.py migrate
```

## 8. Create Superuser
```bash
python manage.py createsuperuser
```

## 9. Reload Web App
- Click "Reload" button in Web tab

## 10. Access Your App
Your app will be available at: yourusername.pythonanywhere.com
