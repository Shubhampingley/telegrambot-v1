import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# Load secrets from GitHub environment
API_KEY     = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD    = os.getenv("ANGEL_PASSWORD")        # M-PIN or 2FA password
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TG_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except:
        pass

def main():
    # Step 1: Generate TOTP
    totp = pyotp.TOTP(TOTP_SECRET).now()

    # Step 2: Initialize SmartConnect
    obj = SmartConnect(api_key=API_KEY)
    
    try:
        session = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
        access_token = session["data"]["accessToken"]
        refresh_token = session["data"]["refreshToken"]
        feed_token = session["data"]["feedToken"]
    except Exception as e:
        send_telegram(f"❌ *Login Failed*\n```{str(e)}```")
        return

    # Step 3: Set tokens
    obj.setAccessToken(access_token)
    obj.setFeedToken(feed_token)

    # Step 4: Call LTP
    try:
        ltp = obj.ltpData("NSE", "RELIANCE", "2885")
        if ltp.get("status"):
            price = ltp["data"]["ltp"]
            send_telegram(f"📈 *RELIANCE LTP:* ₹{price}")
        else:
            send_telegram(f"❌ *LTP fetch failed:*\n```{ltp}```")
    except Exception as e:
        send_telegram(f"❌ *LTP Error:*\n```{str(e)}```")

if __name__ == "__main__":
    main()
