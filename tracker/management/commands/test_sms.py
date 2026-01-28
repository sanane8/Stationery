from django.core.management.base import BaseCommand
from tracker.sms_utils import send_sms, send_whatsapp
import os

class Command(BaseCommand):
    help = 'Test SMS and WhatsApp functionality with current credentials'

    def handle(self, *args, **options):
        self.stdout.write('Testing SMS and WhatsApp credentials...\n')

        # Check if credentials are set
        username = os.getenv('AFRICASTALKING_USERNAME')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        sender_id = os.getenv('AFRICASTALKING_SENDER_ID')

        self.stdout.write(f'Username: {username or "NOT SET"}')
        self.stdout.write(f'API Key: {"SET (" + api_key[:10] + "...)" if api_key else "NOT SET"}')
        self.stdout.write(f'Sender ID: {sender_id or "NOT SET"}')
        self.stdout.write('')

        if not all([username, api_key, sender_id]):
            self.stderr.write(self.style.ERROR('❌ Missing credentials! Please set them in the .env file.'))
            return

        # Test with a dummy phone number (won't actually send)
        test_phone = '+255712345678'  # Dummy Tanzanian number
        test_message = 'Test message from Stationery Tracker'

        # Test SMS
        self.stdout.write(f'Testing SMS send to {test_phone}...')
        sms_result = send_sms(test_phone, test_message)

        if sms_result['success']:
            self.stdout.write(self.style.SUCCESS('✅ SMS credentials are valid!'))
            self.stdout.write(f'SMS Response: {sms_result.get("response", "OK")}')
        else:
            error = sms_result.get('error', 'Unknown error')
            self.stderr.write(self.style.ERROR(f'❌ SMS test failed: {error}'))
            if 'authentication' in error.lower():
                self.stderr.write(self.style.ERROR('Check your username, API key, and sender ID in the .env file.'))

        self.stdout.write('')

        # Test WhatsApp
        self.stdout.write(f'Testing WhatsApp send to {test_phone}...')
        whatsapp_result = send_whatsapp(test_phone, test_message)

        if whatsapp_result['success']:
            self.stdout.write(self.style.SUCCESS('✅ WhatsApp credentials are valid!'))
            self.stdout.write(f'WhatsApp Response: {whatsapp_result.get("response", "OK")}')
        else:
            error = whatsapp_result.get('error', 'Unknown error')
            self.stdout.write(self.style.WARNING(f'⚠️ WhatsApp test: {error}'))
            self.stdout.write(self.style.WARNING('Note: WhatsApp Business API requires separate setup through Africa\'s Talking dashboard'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('SMS test completed! WhatsApp requires additional Business API setup.'))