import africastalking
from django.conf import settings
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def initialize_africastalking():
    """Initialize Africa's Talking SDK"""
    try:
        africastalking.initialize(
            username=settings.AFRICASTALKING_USERNAME,
            api_key=settings.AFRICASTALKING_API_KEY
        )
        return africastalking.SMS
    except Exception as e:
        logger.error(f"Failed to initialize Africa's Talking: {e}")
        return None

def initialize_whatsapp():
    """Initialize Africa's Talking WhatsApp SDK"""
    # Note: Africa's Talking Python SDK doesn't include WhatsApp functionality
    # WhatsApp Business API requires separate setup through their dashboard
    logger.warning("WhatsApp functionality is not available through Africa's Talking Python SDK")
    logger.warning("To use WhatsApp, you need to set up WhatsApp Business API separately")
    return None

def send_sms(phone_number, message):
    """
    Send SMS using Africa's Talking

    Args:
        phone_number (str): Phone number in international format (e.g., +255XXXXXXXXX)
        message (str): SMS message content

    Returns:
        dict: Response containing status and message details
    """
    sms = initialize_africastalking()
    if not sms:
        return {
            'success': False,
            'error': 'SMS service not configured properly'
        }

    try:
        # Ensure phone number starts with +
        if not phone_number.startswith('+'):
            # Assume Tanzanian number if no country code
            if phone_number.startswith('0'):
                phone_number = '+255' + phone_number[1:]
            else:
                phone_number = '+' + phone_number

        response = sms.send(
            message=message,
            recipients=[phone_number],
            sender_id=settings.AFRICASTALKING_SENDER_ID
        )

        logger.info(f"SMS sent to {phone_number}: {response}")

        return {
            'success': True,
            'response': response,
            'recipient': phone_number
        }

    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def send_whatsapp(phone_number, message):
    """
    Send WhatsApp message - Currently not available through Africa's Talking Python SDK

    Args:
        phone_number (str): Phone number in international format (e.g., +255XXXXXXXXX)
        message (str): WhatsApp message content

    Returns:
        dict: Response containing status and message details
    """
    logger.warning("WhatsApp sending attempted but Africa's Talking Python SDK doesn't support WhatsApp")

    return {
        'success': False,
        'error': "WhatsApp Business API is not available through Africa's Talking Python SDK. " +
                "To send WhatsApp messages, you need to set up WhatsApp Business API directly through " +
                "Africa's Talking dashboard or use a third-party WhatsApp service like Twilio."
    }

def send_debt_reminder_sms_for_customer(customer, debts):
    """
    Send debt reminder SMS to customer with all their debts
    
    Args:
        customer: Customer instance
        debts: List of Debt instances for this customer
        
    Returns:
        dict: SMS sending result
    """
    if not customer.phone:
        return {
            'success': False,
            'error': 'Customer has no phone number'
        }
    
    customer_name = customer.name
    
    # Calculate total amount across all debts
    total_amount = sum(debt.amount for debt in debts)
    total_remaining = sum(debt.remaining_amount for debt in debts)
    
    # Get earliest due date
    earliest_due_date = min(debt.due_date for debt in debts)
    earliest_due_str = earliest_due_date.strftime('%d/%m/%Y')
    
    # Check if any debt is overdue
    has_overdue = any(debt.status == 'overdue' for debt in debts)
    
    # Count debts by status
    overdue_count = sum(1 for debt in debts if debt.status == 'overdue')
    pending_count = sum(1 for debt in debts if debt.status == 'pending')
    partial_count = sum(1 for debt in debts if debt.status == 'partial')
    
    # Create message based on debt statuses
    if has_overdue:
        message = f"Habari {customer_name}, una deni la TZS {total_remaining:,.0f} kwa {len(debts)} madeni wake tarehe {earliest_due_str}. Kati {overdue_count} mademi yamekufa, {pending_count} inasubiri, na {partial_count} umeshalipa. Tafadhali lipa haraka ili tusiwe na shida."
    elif pending_count > 0:
        message = f"Habari {customer_name}, una deni la TZS {total_remaining:,.0f} kwa {len(debts)} madeni kabla ya {earliest_due_str}. Tafadhali lipa kwa wakati."
    else:
        message = f"Habari {customer_name}, asante kumekamilipa TZS {total_amount - total_remaining:,.0f} kwa {len(debts)} mademi. Asante kwa malipo yako!"
    
    return send_sms(customer.phone, message)

def send_debt_reminder_sms(debt):
    """
    Send debt reminder SMS to customer

    Args:
        debt: Debt instance

    Returns:
        dict: SMS sending result
    """
    if not debt.customer.phone:
        return {
            'success': False,
            'error': 'Customer has no phone number'
        }

    customer_name = debt.customer.name
    amount = debt.amount
    due_date = debt.due_date.strftime('%d/%m/%Y')
    remaining = debt.remaining_amount

    if debt.status == 'paid':
        message = f"Habari {customer_name}, deni lako la TZS {amount:,.0f} limekwisha lipwa. Asante kwa kufanya biashara nasi."
    elif debt.status == 'overdue':
        message = f"Habari {customer_name}, deni lako la TZS {remaining:,.0f} lilikwisha muda wake tarehe {due_date}. Tafadhali lipa haraka ili tusiwe na shida."
    else:
        message = f"Habari {customer_name}, una deni la TZS {remaining:,.0f} linalotakiwa kulipwa kabla ya {due_date}. Tafadhali lipa kwa wakati."

    return send_sms(debt.customer.phone, message)

def send_debt_reminder_whatsapp(debt):
    """
    Send debt reminder WhatsApp message to customer

    Args:
        debt: Debt instance

    Returns:
        dict: WhatsApp sending result
    """
    if not debt.customer.phone:
        return {
            'success': False,
            'error': 'Customer has no phone number'
        }

    customer_name = debt.customer.name
    amount = debt.amount
    due_date = debt.due_date.strftime('%d/%m/%Y')
    remaining = debt.remaining_amount

    if debt.status == 'paid':
        message = f"🔔 *Habari {customer_name}*\n\n✅ Deni lako la *TZS {amount:,.0f}* limekwisha lipwa.\n\nAsante kwa kufanya biashara nasi! 🙏"
    elif debt.status == 'overdue':
        message = f"🚨 *Habari {customer_name}*\n\n⚠️ Deni lako la *TZS {remaining:,.0f}* lilikwisha muda wake tarehe {due_date}.\n\nTafadhali lipa haraka ili tusiwe na shida. 🏦"
    else:
        message = f"💰 *Habari {customer_name}*\n\nUna deni la *TZS {remaining:,.0f}* linalotakiwa kulipwa kabla ya {due_date}.\n\nTafadhali lipa kwa wakati. ⏰"

    return send_whatsapp(debt.customer.phone, message)