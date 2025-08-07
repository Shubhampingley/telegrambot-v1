import os
import time
import pyotp
import requestsimport os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ─── Configuration ──────────────────────────────────────────────────────────────
API_KEY       = os.getenv("ANGEL_API_KEY")
CLIENT_CODE   = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD      = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET   = os.getenv("ANGEL_TOTP_SECRET")
TELE_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

# ─── Helpers ────────────────────────────────────────────────────────────────────
def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    payload = {"chat_id": TELE_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, data=payload)
        print("Telegram:", r.status_code, r.text)
    except Exception as e:
        print("Telegram error:", e)

# ─── Login & Debug ─────────────────────────────────────────────────────────────
def angel_login():
    try:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        resp = obj.generateSession(
            clientCode=CLIENT_CODE,
            password=PASSWORD,
            totp=totp
        )
        # DEBUG: dump the raw response to Telegram (one-time)
        send_telegram(f"DEBUG Login response:\n```{resp}```")
        if not resp or 'data' not in resp:
            send_telegram("❌ No `data` in login response.")
            return None
        data = resp['data']
        access_token = data.get("accessToken")
        if not access_token:
            send_telegram("❌ No accessToken in response.")
            return None
        obj.setAccessToken(access_token)
        return obj
    except Exception as e:
        send_telegram(f"❌ Angel login exception:\n{e}")
        return None

# ─── Fetch LTP ─────────────────────────────────────────────────────────────────
def get_ltp(obj, symbol, token):
    try:
        res = obj.get_ltp_data(exchange="NSE", tradingsymbol=symbol, symboltoken=token)
        if not res or 'data' not in res:
            return f"Error: invalid LTP response"
        return res['data']['ltp']
    except Exception as e:
        return f"Error: {e}"

# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    obj = angel_login()
    if not obj:
        return

    stocks = [
        {"symbol": "RELIANCE", "token": "2885"},
        {"symbol": "TCS",     "token": "11536"}
    ]
    msg = "📊 *LTP Update:*"
    for s in stocks:
        l = get_ltp(obj, s["symbol"], s["token"])
        msg += f"\n• {s['symbol']}: ₹{l}"
    send_telegram(msg)

if __name__ == "__main__":
    main()

from SmartApi.smartConnect import SmartConnect

# ✅ Load env variables
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ Angel Login Function
def angel_login():
    try:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()

        data = obj.generateSession(clientCode=CLIENT_CODE, password=PASSWORD, totp=totp)
        refreshToken = data['data']['refreshToken']
        userProfile = obj.getProfile(refreshToken)
        return obj
    except Exception as e:
        send_telegram_message(f"❌ Angel login failed:\n{e}")
        return None

# ✅ Telegram Send Function
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

# ✅ Get LTP
def get_ltp(obj, exchange, symbol, token):
    try:
        data = obj.get_ltp_data(exchange=exchange, tradingsymbol=symbol, symboltoken=token)
        return data['data']['ltp']
    except Exception as e:
        return f"Error: {e}"

# ✅ Main Function
def main():
    obj = angel_login()
    if not obj:
        return

    stocks = [
        {"symbol": "RELIANCE", "token": "2885"},
        {"symbol": "TCS", "token": "11536"}
    ]

    message = "📊 *LTP Update:*"
    for stock in stocks:
        ltp = get_ltp(obj, "NSE", stock["symbol"], stock["token"])
        message += f"\n• {stock['symbol']}: ₹{ltp}"

    send_telegram_message(message)

if __name__ == "__main__":
    main()
