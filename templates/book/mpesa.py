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
import threading
from datetime import datetime

# =========================
# M-Pesa Configuration
# =========================
# Load from environment variables, fall back to defaults for sandbox
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', 'xtaExvFW27YoYlReLwIqGAFBf6PfLPBhlmx0PQ1TK9V6Wb7s')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', 'Go0k2BkhrAlKuuAUOWh6dPUSiE6kWhRnSA6bI2mGWrghwZUXjvJyQyC7mZejLii7')
MPESA_SHORT_CODE = os.environ.get('MPESA_SHORT_CODE', '5735986')  # Safaricom test Paybill
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')  # Safaricom test passkey
MPESA_ENVIRONMENT = os.environ.get('MPESA_ENVIRONMENT', 'production')  # 'sandbox' or 'production'
MPESA_CALLBACK_URL = os.environ.get('MPESA_CALLBACK_URL', 'https://curyent.onrender.com/api/mpesa/callback')

# B2C initiator credentials (for payouts)
MPESA_B2C_INITIATOR_NAME = os.environ.get('MPESA_B2C_INITIATOR_NAME', 'YOUR_B2C_INITIATOR')
MPESA_B2C_SECURITY_CREDENTIAL = os.environ.get('MPESA_B2C_SECURITY_CREDENTIAL', 'YOUR_ENCRYPTED_PASSWORD')

# B2C Command IDs
B2C_COMMAND_BUSINESS_PAYMENT = 'BusinessPayment'
B2C_COMMAND_UTILITY_BILL = 'UtilityBill'
B2C_COMMAND_SALARY_PAYMENT = 'SalaryPayment'


def is_configured():
    """Check if M-Pesa credentials are properly configured."""
    return (
        MPESA_CONSUMER_KEY != 'xtaExvFW27YoYlReLwIqGAFBf6PfLPBhlmx0PQ1TK9V6Wb7s' and
        MPESA_CONSUMER_SECRET != 'Go0k2BkhrAlKuuAUOWh6dPUSiE6kWhRnSA6bI2mGWrghwZUXjvJyQyC7mZejLii7' and
        MPESA_SHORT_CODE != '5735986' and
        MPESA_PASSKEY != 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
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


def _send_stk_push_in_background(phone_number, amount, account_reference, transaction_desc, booking_id=None):
    """
    Background thread function to send STK Push via M-Pesa SDK.
    Runs asynchronously so it doesn't block the Flask request.
    """
    try:
        import mpesa
        from mpesa import Config, STKPush, Auth

        # Configure M-Pesa SDK
        config = Config()
        config.CLIENT_KEY = MPESA_CONSUMER_KEY
        config.CLIENT_SECRET = MPESA_CONSUMER_SECRET

        if MPESA_ENVIRONMENT == 'production':
            config.BASE_URL = 'https://api.safaricom.co.ke/mpesa'
        else:
            config.BASE_URL = 'https://sandbox.safaricom.co.ke/mpesa'

        # Get access token
        auth = Auth(config)
        token_response = auth.generate_access_token()

        if 'error' in token_response:
            print(f'[M-Pesa STK] Failed to get access token: {token_response}')
            return

        config.access_token = token_response.get('access_token')

        # Create STK Push payload
        stk = STKPush(config)
        normalized_phone = normalize_phone_number(phone_number)

        payload = stk.create_payload(
            short_code=MPESA_SHORT_CODE,
            pass_key=MPESA_PASSKEY,
            amount=int(amount),
            party_a=normalized_phone,
            party_b=MPESA_SHORT_CODE,
            phone_number=normalized_phone,
            account_reference=account_reference,
            transaction_desc=transaction_desc,
            callback_url=MPESA_CALLBACK_URL,
            transaction_type='CustomerPayBillOnline'
        )

        # Send STK Push
        response = stk.send_stk_push(payload)

        if 'CheckoutRequestID' in response:
            print(f'[M-Pesa STK] Push sent successfully. RequestID: {response["CheckoutRequestID"]}')
            print(f'[M-Pesa STK] ResultCode: {response.get("ResultCode", "N/A")}')
            print(f'[M-Pesa STK] ResultDesc: {response.get("ResultDesc", "N/A")}')
        else:
            print(f'[M-Pesa STK] Error: {response}')

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
    Background thread function to send B2C payment via M-Pesa SDK.
    """
    try:
        import mpesa
        from mpesa import Config, B2C, Auth

        # Configure M-Pesa SDK
        config = Config()
        config.CLIENT_KEY = MPESA_CONSUMER_KEY
        config.CLIENT_SECRET = MPESA_CONSUMER_SECRET

        if MPESA_ENVIRONMENT == 'production':
            config.BASE_URL = 'https://api.safaricom.co.ke/mpesa'
        else:
            config.BASE_URL = 'https://sandbox.safaricom.co.ke/mpesa'

        # Get access token
        auth = Auth(config)
        token_response = auth.generate_access_token()

        if 'error' in token_response:
            print(f'[M-Pesa B2C] Failed to get access token: {token_response}')
            return

        config.access_token = token_response.get('access_token')

        # Create and send B2C payment
        b2c = B2C(config)

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

        response = b2c.make_payment(payload)

        if 'ConversationID' in response or 'ResultCode' in response:
            print(f'[M-Pesa B2C] Payment initiated. Response: {response}')
        else:
            print(f'[M-Pesa B2C] Error: {response}')

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
        result_url = f'{MPESA_CALLBACK_URL}/b2c/result'
    if queue_time_url is None:
        queue_time_url = f'{MPESA_CALLBACK_URL}/b2c/timeout'

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
