from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracker.models import UserProfile


class Command(BaseCommand):
    help = 'Fix admin permissions for existing users'

    def handle(self, *args, **options):
        # Find admin user
        admin_user = User.objects.filter(username='NICKSON').first()
        
        if admin_user:
            # Set Django admin flags
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            
            self.stdout.write(f'Updated Django permissions for {admin_user.username}')
            self.stdout.write(f'Is staff: {admin_user.is_staff}')
            self.stdout.write(f'Is superuser: {admin_user.is_superuser}')
            
            # Check/create UserProfile
            try:
                profile = admin_user.profile
                self.stdout.write(f'Existing profile role: {profile.role}')
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(
                    user=admin_user,
                    role='admin'
                )
                self.stdout.write(f'Created new profile with role: {profile.role}')
            
            self.stdout.write(self.style.SUCCESS('Admin permissions fixed successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Admin user NICKSON not found!'))
