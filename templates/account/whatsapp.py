import os
import random
import africastalking


# =========================
# Africa's Talking SMS Configuration
# =========================
# Africa's Talking sends SMS messages via their API — reliable for Kenyan numbers.
#
# Setup instructions:
#   1. Go to https://africastalking.com and create an account
#   2. Get your API key from the dashboard
#   3. Set the AFRICASTALKING_USERNAME and AFRICASTALKING_API_KEY environment variables
#
# The sender ID "Curyent" will appear as the sender name on recipient phones.
#
# Debug mode: If API key is not set, messages are logged to the console
# instead of being sent, so your app still works during development.

AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME', 'cury')
AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY', 'atsk_3bcc67f1e1091266aa496d3a8be27b1644f2c2305246eadec2989517cbe2d6b1fd9d07a6')
SMS_SENDER_ID = ''  # Empty uses Africa's Talking default; register 'Curyent' as sender ID later at africastalking.com

# Initialize Africa's Talking
if AFRICASTALKING_API_KEY:
    africastalking.initialize(username=AFRICASTALKING_USERNAME, api_key=AFRICASTALKING_API_KEY)
    sms = africastalking.SMS
else:
    sms = None


# =========================
# OTP settings
# =========================
OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_otp():
    """Generate a random 6-digit OTP code."""
    return ''.join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])


def normalize_phone_number(phone_number: str) -> str:
    """
    Normalize Kenyan phone numbers to international format.
    Converts 07xxxxxxxx or 01xxxxxxxx to +2547xxxxxxxx or +2541xxxxxxxx.

    Args:
        phone_number: Phone number in any format (e.g., 0712345678, +254712345678, 254712345678)

    Returns:
        str: Phone number in international format (e.g., +254712345678)
    """
    # Strip whitespace, plus signs, and dashes
    cleaned = phone_number.strip().replace('+', '').replace('-', '').replace(' ', '')

    # If it starts with '07' or '01' (Kenyan local format), convert to +254
    if cleaned.startswith('07') or cleaned.startswith('01'):
        cleaned = '+254' + cleaned[1:]
    # If it starts with '254' but missing '+', add it
    elif cleaned.startswith('254'):
        cleaned = '+' + cleaned
    # Otherwise, if no '+', assume it's a local number and add +254 prefix
    elif not cleaned.startswith('+'):
        cleaned = '+254' + cleaned

    return cleaned


def _send_via_api(phone_number, message_body):
    """
    Send an SMS message using Africa's Talking API.

    Args:
        phone_number: Recipient phone in international format (e.g., +254712345678)
        message_body: The text message to send

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    # If API key is not configured, log the message and return success (debug mode)
    if not AFRICASTALKING_API_KEY or sms is None:
        print(f'[SMS DEBUG] Africa\'s Talking API key not configured — message NOT sent')
        print(f'[SMS DEBUG] To: {phone_number}')
        print(f'[SMS DEBUG] Message: {message_body}')
        return {'success': True, 'message': 'Message logged (Africa\'s Talking not configured)'}

    try:
        # Build send kwargs - only include sender_id if it's set
        send_kwargs = {'sender_id': SMS_SENDER_ID} if SMS_SENDER_ID else {}
        response = sms.send(message_body, [phone_number], **send_kwargs)
        print(f'[SMS] Response: {response}')
        
        # Handle Africa's Talking response format
        if response and 'SMSMessageData' in response:
            msg_data = response['SMSMessageData']
            # Check for error messages
            if msg_data.get('Message') and msg_data['Message'] not in ('', 'Success'):
                error_msg = msg_data['Message']
                print(f'[SMS] Error: {error_msg}')
                return {'success': False, 'message': f'SMS error: {error_msg}'}
            # Check recipients
            recipients = msg_data.get('Recipients', [])
            if recipients:
                for recipient in recipients:
                    if recipient.get('statusCode') == '000':
                        print(f'[SMS] Message sent successfully to {phone_number}')
                        return {'success': True, 'message': 'Message sent via SMS'}
                    else:
                        error_msg = recipient.get('errorMessage', 'Unknown error')
                        print(f'[SMS] Error for {phone_number}: {error_msg}')
                        return {'success': False, 'message': f'SMS error: {error_msg}'}
            # No recipients but no error - might be queued
            print(f'[SMS] Message sent successfully to {phone_number}')
            return {'success': True, 'message': 'Message sent via SMS'}
        
        # Fallback for other response formats
        if response and 'Recipients' in response:
            for recipient in response['Recipients']:
                if recipient.get('statusCode') == '000':
                    print(f'[SMS] Message sent successfully to {phone_number}')
                    return {'success': True, 'message': 'Message sent via SMS'}
                else:
                    error_msg = recipient.get('errorMessage', 'Unknown error')
                    print(f'[SMS] Error for {phone_number}: {error_msg}')
                    return {'success': False, 'message': f'SMS error: {error_msg}'}
        
        print(f'[SMS] Unexpected response format: {response}')
        return {'success': False, 'message': f'Unexpected API response'}

    except Exception as e:
        print(f'[SMS] Failed to send message: {str(e)}')
        return {'success': False, 'message': f'Failed to send: {str(e)}'}


def send_message(phone_number, message_body):
    """
    Send an SMS message using Africa's Talking API.
    Public helper for use by any module (book.py, acc.py, etc.).

    Args:
        phone_number: Recipient phone number (any format)
        message_body: The text message to send

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    # Remove leading zero after country code (e.g., +2540705950970 -> +254705950970)
    if phone_number.startswith('+2540'):
        phone_number = '+254' + phone_number[5:]
    phone_number = normalize_phone_number(phone_number)

    return _send_via_api(phone_number, message_body)


def send_whatsapp_otp(phone_number, otp_code):
    """
    Send OTP via SMS using Africa's Talking API.
    Falls back to debug mode (returns success with OTP in message) if SMS fails.

    Args:
        phone_number: Recipient phone number (e.g., 0712345678, +254712345678)
        otp_code: The 6-digit OTP code to send

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    # Remove leading zero after country code
    if phone_number.startswith('+2540'):
        phone_number = '+254' + phone_number[5:]
    phone_number = normalize_phone_number(phone_number)

    message_body = (
        f'CURYENT Verification\n\n'
        f'Your code: {otp_code}\n\n'
        f'Expires in 5 minutes.\n'
        f'Do not share this code with anyone.'
    )

    print(f'[SMS] Sending OTP to {phone_number}...')
    result = _send_via_api(phone_number, message_body)

    if result['success']:
        print(f'[SMS] OTP sent successfully to {phone_number}')
        return result
    else:
        # Fallback: return success with OTP code in message so the app still works
        # This allows users to see the OTP in the server log or get a helpful message
        print(f'[SMS] SMS failed ({result["message"]}), falling back to debug mode')
        print(f'[SMS] OTP CODE: {otp_code} (for {phone_number})')
        return {
            'success': True,
            'message': f'SMS delivery failed. Your OTP code is: {otp_code}. Please enter this code to continue.',
            'otpFallback': True,
            'otpCode': otp_code
        }


def verify_otp_code(stored_code, user_input):
    """
    Verify if the user-provided OTP matches the stored code.

    Args:
        stored_code: The OTP code stored in the database
        user_input: The code entered by the user

    Returns:
        bool: True if codes match
    """
    return stored_code.strip() == user_input.strip()
