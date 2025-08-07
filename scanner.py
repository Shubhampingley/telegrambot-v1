import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ─── Configuration ──────────────────────────────────────────────────────────────
API_KEY      = os.getenv("ANGEL_API_KEY")
CLIENT_CODE  = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD     = os.getenv("ANGEL_PASSWORD")    # your M-PIN
TOTP_SECRET  = os.getenv("ANGEL_TOTP_SECRET")
TELE_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ─── Telegram Helper ─────────────────────────────────────────────────────────────
def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    payload = {"chat_id": TELE_CHAT_ID, "text": msg}
    try:
        r = requests.post(url, data=payload)
        print("Telegram status:", r.status_code)
    except Exception as e:
        print("Telegram error:", e)

# ─── Startup Debug ───────────────────────────────────────────────────────────────
# Masked debug for ANGEL_PASSWORD presence
pin_present = bool(PASSWORD)
pin_len = len(PASSWORD) if PASSWORD else 0
send_telegram(f"DEBUG: ANGEL_PASSWORD present? {pin_present}, length={pin_len}")

if not PASSWORD:
    send_telegram("❌ ANGEL_PASSWORD (M-PIN) is empty or unset!")
    exit(1)

# ─── Angel Login ─────────────────────────────────────────────────────────────────
def angel_login():
    try:
        client = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        resp = client.generateSession(
            clientCode=CLIENT_CODE,
            password=PASSWORD,
            totp=totp
        )
        # Debug response
        send_telegram(f"DEBUG Login response:\n```{resp}```")
        # Validate response
        if not resp or 'data' not in resp or resp['data'] is None:
            send_telegram("❌ No data in login response.")
            return None
        data = resp['data']
        access_token = data.get('accessToken')
        if not access_token:
            send_telegram("❌ No accessToken in response.")
            return None
        # Set access token for subsequent calls
        client.setAccessToken(access_token)
        return client
    except Exception as e:
        send_telegram(f"❌ Angel login exception:\n{e}")
        return None

# ─── Fetch LTP ───────────────────────────────────────────────────────────────────
def get_ltp(client, symbol, token):
    try:
        res = client.get_ltp_data(exchange="NSE", tradingsymbol=symbol, symboltoken=token)
        if not res or 'data' not in res or res['data'] is None:
            return f"Error: invalid LTP response"
        return res['data'].get('ltp', 'N/A')
    except Exception as e:
        return f"Error: {e}"

# ─── Main Execution ──────────────────────────────────────────────────────────────
def main():
    client = angel_login()
    if not client:
        return

    # List of stocks with their NSE tokens
    stocks = [
        {"symbol": "RELIANCE", "token": "2885"},
        {"symbol": "TCS",       "token": "11536"}
    ]

    message = "📊 *LTP Update:*"
    for s in stocks:
        ltp = get_ltp(client, s['symbol'], s['token'])
        message += f"\n• {s['symbol']}: ₹{ltp}"

    send_telegram(message)

if __name__ == "__main__":
    main()
