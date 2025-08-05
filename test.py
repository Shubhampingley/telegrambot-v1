import os
from telegram import Bot
from SmartApi import SmartConnect
import pyotp

# Load secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Test Telegram
def test_telegram():
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Telegram Bot is working!")
        print("✅ Telegram message sent successfully.")
    except Exception as e:
        print(f"❌ Telegram failed: {e}")

# Test Angel Login
def test_angel_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        session = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
        if "data" in session and session["data"].get("refreshToken"):
            print("✅ Angel API login successful.")
        else:
            print("❌ Angel API login failed.")
    except Exception as e:
        print(f"❌ Angel API error: {e}")

if __name__ == "__main__":
    test_telegram()
    test_angel_login()
