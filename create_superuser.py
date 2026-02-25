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
            user = User.objects.get(username='admin')
            print(f"✅ Superuser 'admin' already exists (ID: {user.id})")
            
            # Verify password
            if user.check_password('admin123'):
                print("✅ Password verified")
            else:
                print("🔧 Updating password...")
                user.set_password('admin123')
                user.save()
                print("✅ Password updated")
            
            return True
        
        # Create superuser
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print(f"✅ Superuser 'admin' created successfully (ID: {user.id})")
        print("📝 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        
        # Verify user can be authenticated
        from django.contrib.auth import authenticate
        test_user = authenticate(username='admin', password='admin123')
        if test_user:
            print("✅ Authentication test passed")
        else:
            print("❌ Authentication test failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_superuser()
    if success:
        print("🎉 Superuser setup completed")
    else:
        print("💥 Superuser setup failed")
        sys.exit(1)
