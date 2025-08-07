import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# Load environment variables
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
MPIN = os.getenv("ANGEL_MPIN")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    return response.status_code

def angel_login():
    try:
        client = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        data = client.generateSession(CLIENT_CODE, MPIN, totp)

        if "data" not in data or "accessToken" not in data["data"]:
            raise Exception(f"❌ Login Failed: {data}")

        auth_token = data["data"]["accessToken"]
        client.setAccessToken(auth_token)
        return client
    except Exception as e:
        send_telegram(f"❌ Exception during login: {str(e)}")
        raise

def main():
    try:
        client = angel_login()
        send_telegram("✅ Angel API login successful")

        # Fetch LTP for NIFTY 50 (token: 99926000)
        ltp = client.ltpData("NSE", "NIFTY", "99926000")
        send_telegram(f"✅ NIFTY LTP: {ltp['data']['ltp']}")
    except Exception as e:
        send_telegram(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
