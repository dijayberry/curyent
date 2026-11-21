"""
M-Pesa payment integration for CURYENT.

Uses mpesa-python-sdk to handle:
  - STK Push (Lipa Na M-Pesa) — customer pays when creating a booking
  - B2C (Business to Customer) — provider receives payout after service approval
  - C2B Callback — handles payment confirmation from M-Pesa

Configuration:
  Set the following environment variables or edit the constants below:
    MPESA_CONSUMER_KEY      — Your M-Pesa app Consumer Key
    MPESA_CONSUMER_SECRET   — Your M-Pesa app Consumer Secret
    MPESA_SHORT_CODE        — Your Paybill/Till number
    MPESA_PASSKEY           — Your M-Pesa passkey for STK Push
    MPESA_ENVIRONMENT       — 'sandbox' (default) or 'production'
    MPESA_CALLBACK_URL      — Public URL for C2B callback (e.g., https://yourdomain.com/api/mpesa/callback)
"""
import os
import base64
import threading
from datetime import datetime

# =========================
# M-Pesa Configuration
# =========================
# Load from environment variables, fall back to real production defaults
# Curyent Till Number: 5735986 | Phone: 0705950970
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'xtaExvFW27YoYlReLwIqGAFBf6PfLPBhlmx0PQ1TK9V6Wb7s')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'Go0k2BkhrAlKuuAUOWh6dPUSiE6kWhRnSA6bI2mGWrghwZUXjvJyQyC7mZejLii7')
MPESA_SHORT_CODE = os.environ.get('MPESA_SHORT_CODE', '5735986')  # Curyent Paybill Till
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')  # Production passkey
MPESA_ENVIRONMENT = os.environ.get('MPESA_ENVIRONMENT', 'production')  # Live production
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', '')  # Auto-detected at runtime if empty

# B2C initiator credentials (for payouts)
MPESA_B2C_INITIATOR_NAME = os.environ.get('MPESA_B2C_INITIATOR_NAME', 'YOUR_B2C_INITIATOR')
MPESA_B2C_SECURITY_CREDENTIAL = os.environ.get('MPESA_B2C_SECURITY_CREDENTIAL', 'YOUR_ENCRYPTED_PASSWORD')

# B2C Command IDs
B2C_COMMAND_BUSINESS_PAYMENT = 'BusinessPayment'
B2C_COMMAND_UTILITY_BILL = 'UtilityBill'
B2C_COMMAND_SALARY_PAYMENT = 'SalaryPayment'


def get_callback_url():
    """
    Get the M-Pesa callback URL.
    Uses the configured URL if set, otherwise auto-detects from the Flask request context.
    """
    if MPESA_CALLBACK_URL:
        return MPESA_CALLBACK_URL

    # Auto-detect from Flask request context
    try:
        from flask import request
        base_url = request.url_root.rstrip('/')
        return base_url + '/api/mpesa/callback'
    except RuntimeError:
        # No request context (e.g., background thread) — use a default
        return 'https://curyent.onrender.com/api/mpesa/callback'


def is_configured():
    """Check if M-Pesa credentials are properly configured."""
    # The default credentials ARE the real production credentials for Curyent
    # Till: 5735986, Phone: 0705950970
    return (
        MPESA_CONSUMER_KEY and
        MPESA_CONSUMER_SECRET and
        MPESA_SHORT_CODE and
        MPESA_PASSKEY
    )


def normalize_phone_number(phone_number: str) -> str:
    """
    Normalize Kenyan phone numbers to M-Pesa format (2547XXXXXXXX).
    M-Pesa API expects numbers without the '+' prefix.

    Args:
        phone_number: Phone number in any format (e.g., 0712345678, +254712345678, 254712345678)

    Returns:
        str: Phone number in M-Pesa format (e.g., 254712345678)
    """
    # Strip whitespace, plus signs, and dashes
    cleaned = phone_number.strip().replace('+', '').replace('-', '').replace(' ', '')

    # Remove leading zero after country code (e.g., 2540705950970 -> 254705950970)
    if cleaned.startswith('2540'):
        cleaned = '254' + cleaned[4:]

    # If it starts with '07' or '01' (Kenyan local format), convert to 254
    if cleaned.startswith('07') or cleaned.startswith('01'):
        cleaned = '254' + cleaned[1:]
    # If it starts with '254' — already correct
    elif cleaned.startswith('254'):
        pass
    # Otherwise, assume it's a local number and add 254 prefix
    else:
        cleaned = '254' + cleaned

    return cleaned


def _get_access_token():
    """
    Get M-Pesa OAuth access token using requests.
    """
    import requests
    from datetime import datetime

    if MPESA_ENVIRONMENT == 'production':
        base_url = 'https://api.safaricom.co.ke'
    else:
        base_url = 'https://sandbox.safaricom.co.ke'

    credentials = f'{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}'
    encoded_creds = base64.b64encode(credentials.encode()).decode()

    response = requests.get(
        f'{base_url}/oauth/v1/generate?grant_type=client_credentials',
        headers={'Authorization': f'Basic {encoded_creds}'},
        timeout=10
    )

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f'[M-Pesa] Failed to get access token: {response.text}')
        return None


def _send_stk_push_in_background(phone_number, amount, account_reference, transaction_desc, booking_id=None):
    """
    Background thread function to send STK Push using requests.
    Runs asynchronously so it doesn't block the Flask request.
    """
    import requests
    from datetime import datetime

    try:
        # Get access token
        access_token = _get_access_token()
        if not access_token:
            print('[M-Pesa STK] Failed to get access token')
            return

        if MPESA_ENVIRONMENT == 'production':
            base_url = 'https://api.safaricom.co.ke/mpesa'
        else:
            base_url = 'https://sandbox.safaricom.co.ke/mpesa'

        normalized_phone = normalize_phone_number(phone_number)

        # Generate timestamp and password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f'{MPESA_SHORT_CODE}{MPESA_PASSKEY}{timestamp}'
        password = base64.b64encode(password_string.encode()).decode()

        # Build STK Push payload
        payload = {
            'BusinessShortCode': MPESA_SHORT_CODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': normalized_phone,
            'PartyB': MPESA_SHORT_CODE,
            'PhoneNumber': normalized_phone,
            'CallBackURL': get_callback_url(),
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        # Send STK Push
        response = requests.post(
            f'{base_url}/stkpush/v1/processrequest',
            json=payload,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=15
        )

        result = response.json()
        if 'CheckoutRequestID' in result:
            print(f'[M-Pesa STK] Push sent successfully. RequestID: {result["CheckoutRequestID"]}')
            print(f'[M-Pesa STK] ResultCode: {result.get("ResultCode", "N/A")}')
            print(f'[M-Pesa STK] ResultDesc: {result.get("ResultDesc", "N/A")}')
        else:
            print(f'[M-Pesa STK] Error: {result}')

    except Exception as e:
        print(f'[M-Pesa STK] Failed to send STK Push: {str(e)}')


def initiate_stk_push(phone_number, amount, account_reference='CURYENT', transaction_desc='Booking Payment', booking_id=None):
    """
    Initiate an STK Push (Lipa Na M-Pesa) for a booking payment.

    The customer will receive a prompt on their phone to enter M-Pesa PIN
    and complete the payment.

    Args:
        phone_number: Customer's phone number (e.g., 0712345678, +254712345678)
        amount: Payment amount in KES
        account_reference: Reference shown on M-Pesa statement (e.g., booking ID)
        transaction_desc: Description of the transaction
        booking_id: Optional booking ID for tracking

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    if not is_configured():
        print('[M-Pesa STK] Not configured — skipping STK Push (set your credentials)')
        return {
            'success': True,
            'message': 'M-Pesa not configured — payment simulated in development mode',
            'simulated': True
        }

    normalized_phone = normalize_phone_number(phone_number)
    print(f'[M-Pesa STK] Initiating STK Push for {normalized_phone}, amount: KES {amount}')

    # Send STK Push in a background thread so the API response is not blocked
    thread = threading.Thread(
        target=_send_stk_push_in_background,
        args=(phone_number, amount, account_reference, transaction_desc, booking_id),
        daemon=True
    )
    thread.start()

    return {
        'success': True,
        'message': 'M-Pesa payment prompt sent to your phone. Please enter your M-Pesa PIN to complete payment.',
        'phone': normalized_phone,
        'amount': amount
    }


def _send_b2c_in_background(queues_account, recipient_phone, amount, result_url, queue_time_url, command_id=B2C_COMMAND_BUSINESS_PAYMENT, occasion='Service Payout'):
    """
    Background thread function to send B2C payment using requests.
    """
    import requests

    try:
        # Get access token
        access_token = _get_access_token()
        if not access_token:
            print('[M-Pesa B2C] Failed to get access token')
            return

        if MPESA_ENVIRONMENT == 'production':
            base_url = 'https://api.safaricom.co.ke/mpesa'
        else:
            base_url = 'https://sandbox.safaricom.co.ke/mpesa'

        payload = {
            'InitiatorName': MPESA_B2C_INITIATOR_NAME,
            'SecurityCredential': MPESA_B2C_SECURITY_CREDENTIAL,
            'CommandID': command_id,
            'Amount': int(amount),
            'PartyA': MPESA_SHORT_CODE,
            'PartyB': normalize_phone_number(recipient_phone),
            'Remarks': occasion,
            'QueueTimeOutURL': queue_time_url,
            'ResultURL': result_url,
            'Occasion': occasion
        }

        response = requests.post(
            f'{base_url}/b2c/v1/paymentrequest',
            json=payload,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=15
        )

        result = response.json()
        if 'ConversationID' in result or 'ResultCode' in result:
            print(f'[M-Pesa B2C] Payment initiated. Response: {result}')
        else:
            print(f'[M-Pesa B2C] Error: {result}')

    except Exception as e:
        print(f'[M-Pesa B2C] Failed to send B2C payment: {str(e)}')


def initiate_b2c_payout(recipient_phone, amount, result_url=None, queue_time_url=None, occasion='Service Payout'):
    """
    Initiate a B2C (Business to Customer) payout to a provider.

    Used to pay service providers after their service is approved.

    Args:
        recipient_phone: Provider's phone number
        amount: Payout amount in KES
        result_url: URL to receive result callback
        queue_time_url: URL to receive timeout callback
        occasion: Description of the payout

    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    if not is_configured():
        print('[M-Pesa B2C] Not configured — skipping B2C payout (set your credentials)')
        return {
            'success': True,
            'message': 'M-Pesa not configured — payout simulated in development mode',
            'simulated': True
        }

    if not MPESA_B2C_INITIATOR_NAME or MPESA_B2C_INITIATOR_NAME == 'YOUR_B2C_INITIATOR':
        print('[M-Pesa B2C] B2C initiator not configured — skipping payout')
        return {
            'success': True,
            'message': 'B2C payout not configured — payout simulated in development mode',
            'simulated': True
        }

    normalized_phone = normalize_phone_number(recipient_phone)
    print(f'[M-Pesa B2C] Initiating payout of KES {amount} to {normalized_phone}')

    if result_url is None:
        result_url = f'{get_callback_url()}/b2c/result'
    if queue_time_url is None:
        queue_time_url = f'{get_callback_url()}/b2c/timeout'

    # Send B2C in a background thread
    thread = threading.Thread(
        target=_send_b2c_in_background,
        args=(MPESA_SHORT_CODE, recipient_phone, amount, result_url, queue_time_url, B2C_COMMAND_BUSINESS_PAYMENT, occasion),
        daemon=True
    )
    thread.start()

    return {
        'success': True,
        'message': 'M-Pesa payout initiated. Provider will receive payment shortly.',
        'phone': normalized_phone,
        'amount': amount
    }


def handle_c2b_callback(data):
    """
    Handle C2B callback from M-Pesa after a customer completes payment.

    M-Pesa sends a callback with transaction details. This function processes
    the callback and returns the relevant data for updating booking status.

    Args:
        data: The callback data from M-Pesa

    Returns:
        dict with transaction details including result code and message
    """
    if not data:
        return {'success': False, 'message': 'No callback data'}

    # Extract transaction details from callback
    # The callback structure varies between Validation and Confirmation
    result_type = data.get('ResultType', 0)
    result_code = data.get('ResultCode', 0)
    result_desc = data.get('ResultDesc', '')

    # Confirmation callback (ResultType = 1)
    if result_type == 1:
        transaction = {
            'result_code': result_code,
            'result_desc': result_desc,
            'transaction_id': data.get('TransactionID', ''),
            'trade_type': data.get('TradeType', ''),
            'amount': data.get('Amount', 0),
            'sender_number': data.get('MSISDN', ''),
            'bill_ref': data.get('BillNumber', ''),
            'transaction_date': data.get('TransactionDate', 0),
        }

        # Check if payment was successful (ResultCode 0 = success)
        if result_code == 0:
            transaction['success'] = True
            transaction['message'] = 'Payment confirmed'
            print(f'[M-Pesa C2B] Payment confirmed: KES {transaction["amount"]} from {transaction["sender_number"]}')
        else:
            transaction['success'] = False
            transaction['message'] = f'Payment failed: {result_desc}'
            print(f'[M-Pesa C2B] Payment failed: {result_desc}')

        return transaction
    else:
        print(f'[M-Pesa C2B] Non-confirmation callback received: {data}')
        return {'success': False, 'message': 'Non-confirmation callback'}
