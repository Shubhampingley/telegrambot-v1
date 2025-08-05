import os
from telegram import Bot
from dotenv import load_dotenv

# Load .env or GitHub Secrets
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Debug logs
print(f"✅ DEBUG — TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")
print(f"✅ DEBUG — TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")

def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Message sent to Telegram")
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")

# 🔁 Test run
def test():
    message = "✅ Test Successful! Your Angel-based scanner is working."
    send_telegram_message(message)

if __name__ == "__main__":
    test()
