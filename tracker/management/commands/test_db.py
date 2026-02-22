from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Test database connection and show connection info'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing database connection...'))
        
        try:
            # Test basic connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    self.stdout.write(self.style.SUCCESS('✅ Database connection successful!'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Database connection failed'))
                    return
            
            # Show database info
            self.stdout.write(self.style.SUCCESS('\n📊 Database Information:'))
            self.stdout.write(f'   Engine: {settings.DATABASES["default"]["ENGINE"]}')
            self.stdout.write(f'   Name: {settings.DATABASES["default"]["NAME"]}')
            self.stdout.write(f'   Host: {settings.DATABASES["default"]["HOST"]}')
            self.stdout.write(f'   Port: {settings.DATABASES["default"]["PORT"]}')
            self.stdout.write(f'   User: {settings.DATABASES["default"]["USER"]}')
            
            # Test some queries
            self.stdout.write(self.style.SUCCESS('\n🔍 Testing queries...'))
            
            # Check if tables exist
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                self.stdout.write(f'   📋 Found {len(tables)} tables:')
                for table in tables[:10]:  # Show first 10 tables
                    self.stdout.write(f'      - {table[0]}')
                if len(tables) > 10:
                    self.stdout.write(f'      ... and {len(tables) - 10} more')
            
            # Check user count
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                self.stdout.write(f'   👥 Users in database: {user_count}')
            
            # Check shop count
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM tracker_shop")
                shop_count = cursor.fetchone()[0]
                self.stdout.write(f'   🏪 Shops in database: {shop_count}')
            
            self.stdout.write(self.style.SUCCESS('\n🎉 Database is fully operational!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Database connection failed: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'   Error type: {type(e).__name__}'))
