#!/usr/bin/env python3
"""
Prepare Stationery Management System for PythonAnywhere deployment
This creates a deployment package with all necessary files
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_deployment_package():
    """Create a zip file ready for PythonAnywhere upload"""
    
    print("📦 Creating deployment package for PythonAnywhere...")
    
    # Create deployment directory
    deploy_dir = Path("stationery_pythonanywhere")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Files to exclude
    exclude_files = {
        '.git', '.venv', '__pycache__', 'db.sqlite3', 
        'staticfiles', '.env', 'backup.sh', 'deploy_*.py',
        'stationery_tracker', 'templates/tracker'
    }
    
    # Copy essential files
    essential_files = [
        'tracker', 'templates', 'static', 'manage.py',
        'requirements_pythonanywhere.txt', 'pythonanywhere_wsgi.py',
        'stationery_tracker'
    ]
    
    for item in essential_files:
        src = Path(item)
        if src.exists():
            if src.is_dir():
                shutil.copytree(src, deploy_dir / src.name, 
                              ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            else:
                shutil.copy2(src, deploy_dir)
            print(f"✅ Copied {item}")
    
    # Create .env file template
    env_template = """# PythonAnywhere Environment Variables
SECRET_KEY=generate-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.pythonanywhere.com
DATABASE_URL=sqlite:///home/yourusername/Stationery/db.sqlite3
"""
    
    with open(deploy_dir / ".env.example", "w") as f:
        f.write(env_template)
    
    print("✅ Created .env.example")
    
    # Create deployment instructions
    instructions = """
# PythonAnywhere Quick Deployment

## 1. Upload Files
- Upload this entire folder to PythonAnywhere
- Use the "Files" tab -> "Upload a file or directory"

## 2. Set Up Virtual Environment
In PythonAnywhere Bash console:
```bash
mkvirtualenv --python=python3.11 stationery
workon stationery
pip install -r requirements_pythonanywhere.txt
```

## 3. Configure Database
```bash
cd ~/stationery_pythonanywhere
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 4. Configure Web App
- Go to "Web" tab
- Create new web app -> Manual Configuration
- Python version: 3.11
- Working directory: /home/yourusername/stationery_pythonanywhere
- WSGI file: /home/yourusername/stationery_pythonanywhere/pythonanywhere_wsgi.py
- Virtualenv: /home/yourusername/.virtualenvs/stationery
- Click "Reload"
"""
    
    with open(deploy_dir / "DEPLOY_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    
    # Create zip file
    zip_filename = "stationery_pythonanywhere.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in deploy_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"🎉 Created {zip_filename} - Ready for upload!")
    print(f"📁 Package size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    
    return zip_filename

if __name__ == "__main__":
    create_deployment_package()
