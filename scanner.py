# scanner.py
import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

def send_telegram(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        r = requests.post(url, data=data)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram error:", e)

def test_angel_login():
    try:
        obj = SmartConnect(api_key=os.getenv("ANGEL_API_KEY"))
        totp = pyotp.TOTP(os.getenv("ANGEL_TOTP_SECRET")).now()

        data = obj.generateSession(
            client_id=os.getenv("ANGEL_CLIENT_CODE"),
            password=os.getenv("ANGEL_PASSWORD"),
            totp=totp
        )

        if 'data' in data and 'feedToken' in data:
            send_telegram("✅ Angel API login successful!")
        else:
            send_telegram("⚠️ Angel login returned no feedToken.")
    except Exception as e:
        send_telegram(f"❌ Angel login failed:\n{e}")

if __name__ == "__main__":
    test_angel_login()
