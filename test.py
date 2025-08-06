import os
import pyotp
import requests
from telegram import Bot

# Load secrets
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_MPIN        = os.getenv("ANGEL_MPIN")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def test_login():
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
    url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/userauth/v1/loginByPin"
    headers = {"X-API-Key": ANGEL_API_KEY, "Content-Type": "application/json"}
    payload = {
        "clientcode": ANGEL_CLIENT_CODE,
        "mpin": ANGEL_MPIN,
        "totp": totp
    }
    resp = requests.post(url, json=payload, headers=headers).json()
    send(f"🔍 LOGIN RESPONSE:\n{resp}")
    if resp.get("status") and resp["data"].get("jwtToken"):
        send("✅ Angel One MPIN Login Successful!")
    else:
        send("❌ Angel One MPIN Login Failed.")

if __name__ == "__main__":
    test_login()
