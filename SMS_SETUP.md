# SMS & WhatsApp Setup Instructions

To enable SMS and WhatsApp functionality for debt reminders, you need to set up Africa's Talking API credentials.

## 1. Create Africa's Talking Account
1. Go to https://account.africastalking.com/
2. Sign up for an account if you don't have one
3. Verify your email and phone number

## 2. Get API Credentials
1. Log in to your Africa's Talking dashboard
2. Go to **Settings > API Key**
3. Copy your:
   - **Username**
   - **API Key**
4. Go to **Settings > SMS > Sender IDs**
5. Create a new Sender ID (e.g., your business name like "STATIONERY" or "DUKA")
6. Wait for approval (usually instant for alphanumeric sender IDs)

## 3. Configure Credentials
A `.env` file has been created in your project root. Edit it with your actual credentials:

```
AFRICASTALKING_USERNAME=your_actual_username
AFRICASTALKING_API_KEY=your_actual_api_key
AFRICASTALKING_SENDER_ID=your_actual_sender_id
```

## 4. WhatsApp Business API Setup (Currently Unavailable)
**Important:** Africa's Talking Python SDK does not currently support WhatsApp messaging. To send WhatsApp messages, you would need to:

1. Apply for WhatsApp Business API access through Africa's Talking dashboard
2. Set up a WhatsApp Business Account
3. Use their web interface or REST API directly
4. This requires separate approval and has additional costs

**Current Status:** WhatsApp buttons are available in the interface but will show setup instructions. Use SMS for immediate functionality.

## Alternative WhatsApp Solutions:
- **Twilio WhatsApp API**: More reliable, works worldwide
- **360Dialog**: WhatsApp Business API provider
- **MessageBird**: Another WhatsApp API provider

For now, **SMS functionality works immediately** with your Africa's Talking account.

## 5. Install Dependencies
Run: `pip install -r requirements.txt`

## 6. Test Your Credentials
After setting up your credentials in the `.env` file, test them:

```bash
python manage.py test_sms
```

This will verify your SMS and WhatsApp credentials without sending actual messages.

## 7. Test SMS & WhatsApp Functionality
1. Restart your Django server: `python manage.py runserver`
2. Go to a debt detail page
3. Click "Send Reminder" dropdown and choose SMS or WhatsApp
4. For bulk sending, go to Debts list and use "Send Bulk Reminders"

## Phone Number Format
- Customer phone numbers should be in international format: +255XXXXXXXXX
- If entered as 0XXXXXXXXX, the system will automatically convert to +255XXXXXXXXX
- Make sure customer phone numbers are updated in the system

## Message Types

### SMS Messages (Plain Text)
- **Pending/Partial**: Reminder to pay before due date
- **Overdue**: Urgent reminder that payment is overdue
- **Paid**: Confirmation that debt is fully paid

### WhatsApp Messages (Rich Text with Emojis)
- **Pending/Partial**: 💰 *Habari [Name]* - Una deni la *TZS [Amount]*...
- **Overdue**: 🚨 *Habari [Name]* - ⚠️ Deni lako lilikwisha muda...
- **Paid**: 🔔 *Habari [Name]* - ✅ Deni lako limekwisha lipwa...

## Troubleshooting
- Check that API credentials are correct in the `.env` file
- Ensure you have SMS credits in your Africa's Talking account
- For WhatsApp, ensure you have WhatsApp Business API approval
- Verify customer phone numbers are in the correct format
- Check Django logs for any error messages
- Restart Django server after changing `.env` file

## Cost Comparison
- **SMS**: Typically cheaper, works with any phone number
- **WhatsApp**: More expensive, requires WhatsApp Business API setup, but higher engagement rates
- Restart Django server after changing `.env` file
- Verify customer phone numbers are in the correct format
- Check Django logs for any error messages