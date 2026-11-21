import os
import random
import requests


# =========================
# Wasender API Configuration
# =========================
# Wasender API sends WhatsApp messages via HTTP — no browser needed.
#
# Setup instructions:
#   1. Go to https://wasenderapi.com and create an account
#   2. Connect your WhatsApp by scanning the QR code
#   3. Generate an API key from your Wasender dashboard
#   4. Set the WASENDER_API_KEY environment variable
#
# The sender name "Curyent" will appear as the contact name for recipients
# who have saved your number, or as the display name on the Wasender device.
#
# Debug mode: If API key is not set, messages are logged to the console
# instead of being sent, so your app still works during development.

WASENDER_API_URL = 'https://api.wasenderapi.com/api/send-message'
WASENDER_API_KEY = os.environ.get('WASENDER_API_KEY', '6d2cd6b6f85f4defd517d1b6b8cba0f42c5f3cf957bad3a91de74b7b4c16ab7a')


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
    Send a WhatsApp message using the Wasender API.

    Args:
        phone_number: Recipient phone in international format (e.g., +254712345678)
        message_body: The text message to send

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    # If API key is not configured, log the message and return success (debug mode)
    if not WASENDER_API_KEY:
        print(f'[WhatsApp DEBUG] Wasender API key not configured — message NOT sent')
        print(f'[WhatsApp DEBUG] To: {phone_number}')
        print(f'[WhatsApp DEBUG] Message: {message_body}')
        return {'success': True, 'message': 'Message logged (Wasender not configured)'}

    payload = {
        'to': phone_number,
        'text': message_body
    }

    headers = {
        'Authorization': f'Bearer {WASENDER_API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            WASENDER_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f'[WhatsApp] Message sent successfully to {phone_number}')
            return {'success': True, 'message': 'Message sent via WhatsApp'}
        else:
            # Print full response body for debugging
            print(f'[WhatsApp] API error ({response.status_code}): {response.text}')
            try:
                error_data = response.json()
                error_detail = error_data.get('message', error_data.get('error', 'Unknown error'))
            except Exception:
                error_detail = response.text[:200]
            print(f'[WhatsApp] Error detail: {error_detail}')
            return {'success': False, 'message': f'API error: {error_detail}'}

    except requests.exceptions.Timeout:
        print(f'[WhatsApp] Request timed out for {phone_number}')
        return {'success': False, 'message': 'Request timed out'}
    except requests.exceptions.ConnectionError:
        print(f'[WhatsApp] Connection error for {phone_number}')
        return {'success': False, 'message': 'Connection error'}
    except Exception as e:
        print(f'[WhatsApp] Failed to send message: {str(e)}')
        return {'success': False, 'message': f'Failed to send: {str(e)}'}


def send_message(phone_number, message_body):
    """
    Send a WhatsApp message using the Wasender API.
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
    Send OTP via WhatsApp using the Wasender API.

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

    print(f'[WhatsApp] Sending OTP to {phone_number}...')
    result = _send_via_api(phone_number, message_body)

    if result['success']:
        print(f'[WhatsApp] OTP sent successfully to {phone_number}')

    return result


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
