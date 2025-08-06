import os
import pyotp
from telegram import Bot
from SmartApi import SmartConnect

# Load from env / GitHub Secrets
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD    = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    except:
        print("Failed to send Telegram message")

def test_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        resp = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
        # Print to console
        print("🔍 LOGIN RESPONSE:", resp)
        # And send via Telegram
        send(f"🔍 LOGIN RESPONSE:\n{resp}")
    except Exception as e:
        print("❌ Exception:", e)
        send(f"❌ Exception in login: {e}")

if __name__ == "__main__":
    test_login()
