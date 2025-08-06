import os
import pyotp
from telegram import Bot
from SmartApi import SmartConnect

# load from ENV
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD    = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def test_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        response = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)

        # Print full response to console
        print("🔍 FULL LOGIN RESPONSE:", response)

        # Also send it to Telegram (truncate if too big)
        short = str(response)
        if len(short) > 4000:
            short = short[:4000] + "...(truncated)"
        send(f"🔍 LOGIN RESPONSE:\n{short}")

        if response and response.get("data", {}).get("refreshToken"):
            send("✅ Angel One Login Successful!")
        else:
            send("❌ Angel One Login Failed — check the response above.")

    except Exception as e:
        print("❌ Exception during login:", e)
        send(f"❌ Exception in test_login: {e}")

if __name__ == "__main__":
    test_login()
