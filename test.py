import os
import pyotp
from telegram import Bot
from SmartApi import SmartConnect

# Load from ENV
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
    try:
        api = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        # MPIN login
        resp = api.generateSession(clientcode=ANGEL_CLIENT_CODE, mpin=ANGEL_MPIN, totp=totp)
        print("🔍 LOGIN RESPONSE:", resp)
        short = str(resp)
        if len(short) > 4000: short = short[:4000] + "...(truncated)"
        send(f"🔍 LOGIN RESPONSE:\n{short}")
        if resp.get("data", {}).get("refreshToken"):
            send("✅ Angel One MPIN Login Successful!")
        else:
            send("❌ Angel One MPIN Login Failed.")
    except Exception as e:
        print("❌ Exception:", e)
        send(f"❌ Exception in test_login: {e}")

if __name__ == "__main__":
    test_login()
