from telegram import Bot
import os

# Fetch tokens from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    print(f"📤 Sending Telegram Message: {message}")
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def test():
    send_telegram_message("✅ Test Successful! Your Angel-based scanner is working.")

if __name__ == "__main__":
    test()
