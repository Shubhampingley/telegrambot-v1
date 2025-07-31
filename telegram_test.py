import requests

TELEGRAM_BOT_TOKEN = '8116462125:AAF-Nw313C1vew8Y96InHWJBXX9VnwbxFFc'
TELEGRAM_CHAT_ID = '665594180'

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    res = requests.post(url, json=payload)
    print(f"Telegram status: {res.status_code}")
    print(f"Telegram response: {res.text}")

send_telegram("🚨 Forced Test: This is a manual message from your scanner bot")
