#!/usr/bin/env python
"""
Create superuser for Railway deployment
"""

import os
import sys
import django

# Add project directory to Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.production_settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Create superuser if it doesn't exist"""
    
    print("🔧 Creating superuser...")
    
    try:
        # Check if superuser already exists
        if User.objects.filter(username='admin').exists():
            print("✅ Superuser 'admin' already exists")
            return True
        
        # Create superuser
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✅ Superuser 'admin' created successfully")
        print("📝 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return False

if __name__ == "__main__":
    success = create_superuser()
    if success:
        print("🎉 Superuser setup completed")
    else:
        print("💥 Superuser setup failed")
        sys.exit(1)
