import requests

TELEGRAM_BOT_TOKEN = '8116462125:AAF-Nw313C1vew8Y96InHWJBXX9VnwbxFFc'
TELEGRAM_CHAT_ID = '665594180'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    print(f"Telegram response: {response.text}")

# TEST MESSAGE
send_telegram_message("✅ Test Message: NSE Scanner is working perfectly!")
