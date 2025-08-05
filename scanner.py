import os
from telegram import Bot
from datetime import datetime

# Load secrets from GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def test():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"✅ Telegram Test Successful!\n\nTime: {now}"
    send_telegram_message(message)

if __name__ == "__main__":
    test()
