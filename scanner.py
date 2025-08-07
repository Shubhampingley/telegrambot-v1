# scanner.py
import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

def send_telegram(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=data)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram error:", e)

def login_angel():
    try:
        obj = SmartConnect(api_key=os.getenv("ANGEL_API_KEY"))
        totp = pyotp.TOTP(os.getenv("ANGEL_TOTP_SECRET")).now()
        data = obj.generateSession(
            clientCode=os.getenv("ANGEL_CLIENT_CODE"),
            password=os.getenv("ANGEL_PASSWORD"),
            totp=totp
        )
        return obj
    except Exception as e:
        send_telegram(f"❌ Angel login failed:\n{e}")
        return None

def get_ltp(obj, exchange, symbol):
    try:
        search_result = obj.searchScrip(exchange, symbol)
        token = search_result['data']['token']
        quote = obj.ltpData(exchange, token)
        return quote['data']['ltp']
    except Exception as e:
        return f"Error: {e}"

def main():
    obj = login_angel()
    if obj is None:
        return

    stocks = [("NSE", "RELIANCE"), ("NSE", "TCS")]
    msg_lines = ["📊 *LTP Update:*"]

    for exchange, symbol in stocks:
        ltp = get_ltp(obj, exchange, symbol)
        msg_lines.append(f"• {symbol}: ₹{ltp}")

    send_telegram("\n".join(msg_lines))

if __name__ == "__main__":
    main()
