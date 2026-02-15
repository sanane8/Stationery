import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stationery_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from tracker.models import UserProfile

print("=== Checking Admin User ===")

# Find admin user
admin_user = User.objects.filter(username='NICKSON').first()
if admin_user:
    print(f"✅ Admin user found: {admin_user.username}")
    print(f"   Email: {admin_user.email}")
    print(f"   Is staff: {admin_user.is_staff}")
    print(f"   Is superuser: {admin_user.is_superuser}")
    print(f"   Is active: {admin_user.is_active}")
    
    # Check UserProfile
    try:
        profile = admin_user.profile
        print(f"✅ UserProfile found:")
        print(f"   Role: {profile.role}")
        print(f"   Is admin: {profile.is_admin()}")
        print(f"   Phone: {profile.phone}")
    except UserProfile.DoesNotExist:
        print("❌ No UserProfile found - creating one...")
        profile = UserProfile.objects.create(
            user=admin_user,
            role='admin'
        )
        print(f"✅ Created UserProfile with role: {profile.role}")
    
    # Fix Django permissions if needed
    if not admin_user.is_staff or not admin_user.is_superuser:
        print("🔧 Fixing Django permissions...")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print("✅ Django permissions fixed!")
    
else:
    print("❌ Admin user NICKSON not found!")
    print("Creating admin user...")
    admin_user = User.objects.create_user(
        username='NICKSON',
        email='admin@example.com',
        password='admin123',
        is_staff=True,
        is_superuser=True
    )
    UserProfile.objects.create(
        user=admin_user,
        role='admin'
    )
    print("✅ Admin user created!")

print("\n=== Test Admin Access ===")
try:
    profile = admin_user.profile
    print(f"User: {admin_user.username}")
    print(f"Role: {profile.role}")
    print(f"Can access admin: {profile.is_admin()}")
    print("✅ All checks passed!")
except Exception as e:
    print(f"❌ Error: {e}")
