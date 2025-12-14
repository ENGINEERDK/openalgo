import httpx
import hashlib
import json
import os
from dotenv import load_dotenv
from utils.httpx_client import get_httpx_client

try:
    import pyotp
except Exception:
    pyotp = None

load_dotenv()


def sha256_hash(text: str) -> str:
    """Generate SHA256 hash."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def authenticate_broker(userid: str | None = None, password: str | None = None, totp_code: str | None = None):
    """
    Authenticate with Shoonya and return the auth token.

    This function is backward compatible. If any of the parameters are None,
    it will attempt to read values from environment variables:
      - BROKER_USERID
      - BROKER_PASSWORD
      - BROKER_TOTP_SECRET (used to generate a TOTP if totp_code is not provided)

    Returns:
      (susertoken, None) on success
      (None, error_message) on failure
    """
    # Allow passing credentials via environment (.env)
    if not userid:
        userid = os.getenv('BROKER_USERID')
    if not password:
        password = os.getenv('BROKER_PASSWORD')

    # If totp_code not provided, try generating from secret in env
    if not totp_code:
        totp_secret = os.getenv('BROKER_TOTP_SECRET')
        if totp_secret:
            if pyotp is None:
                return None, 'pyotp is required to generate TOTP; please install pyotp'
            try:
                totp_code = pyotp.TOTP(totp_secret).now()
            except Exception as e:
                return None, f'Failed to generate TOTP from secret: {e}'

    # Validate required values
    if not userid or not password:
        return None, 'Missing userid or password. Provide them as arguments or set BROKER_USERID and BROKER_PASSWORD in the environment.'

    # Get the Shoonya API key and other credentials from environment variables
    api_secretkey = os.getenv('BROKER_API_SECRET')
    vendor_code = os.getenv('BROKER_API_KEY')
    imei = os.getenv('BROKER_IMEI', 'abc1234')  # Default IMEI if not provided

    try:
        # Shoonya API login URL
        url = "https://api.shoonya.com/NorenWClientTP/QuickAuth"

        # Prepare login payload
        payload = {
            "uid": userid,  # User ID
            "pwd": sha256_hash(password),  # SHA256 hashed password
            "factor2": totp_code,  # PAN or TOTP or DOB (second factor)
            "apkversion": "1.0.0",  # API version (as per Shoonya's requirement)
            "appkey": sha256_hash(f"{userid}|{api_secretkey}"),  # SHA256 of uid and API key
            "imei": imei,  # IMEI or MAC address
            "vc": vendor_code,  # Vendor code
            "source": "API"  # Source of login request
        }

        # Convert payload to string with 'jData=' prefix
        payload_str = "jData=" + json.dumps(payload)

        # Set headers for the API request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Get the shared httpx client and send the POST request to Shoonya's API
        client = get_httpx_client()
        response = client.post(url, data=payload_str, headers=headers)

        # Handle the response
        if response.status_code == 200:
            data = response.json()
            if data.get('stat') == "Ok":
                return data.get('susertoken'), None  # Return the token on success
            else:
                return None, data.get('emsg', 'Authentication failed. Please try again.')
        else:
            return None, f"Error: {response.status_code}, {response.text}"

    except Exception as e:
        return None, str(e)