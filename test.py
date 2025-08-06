import os
from telegram import Bot
from SmartApi import SmartConnect
import pyotp

# Load secrets from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def test_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        response = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)

        # Check if login was successful
        if 'data' in response and 'refreshToken' in response['data']:
            send_telegram_message("✅ Angel One Login Successful!")
        else:
            send_telegram_message(f"❌ Angel Login Failed. Response: {response}")

    except Exception as e:
        send_telegram_message(f"❌ Error in Test: {str(e)}")

if __name__ == "__main__":
    test_login()
