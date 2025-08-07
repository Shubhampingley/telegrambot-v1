import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ─── Configuration ──────────────────────────────────────────────────────────────
API_KEY     = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD    = os.getenv("ANGEL_PASSWORD")    # your M-PIN
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TG_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

# ─── Helpers ────────────────────────────────────────────────────────────────────
def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=payload)
        print("Telegram status:", r.status_code)
    except Exception as e:
        print("Telegram error:", e)

# ─── Main ────────────────────────────────────────────────────────────────────────
def main():
    # 1) Login to Angel One
    client = SmartConnect(api_key=API_KEY)
    totp   = pyotp.TOTP(TOTP_SECRET).now()
    resp   = client.generateSession(
        clientCode=CLIENT_CODE,
        password=PASSWORD,
        totp=totp
    )

    # Validate login response
    data = resp.get("data") or {}
    access_token = data.get("accessToken")
    if not access_token:
        send_telegram(f"❌ Angel login failed:\n```{resp}```")
        return
    client.setAccessToken(access_token)

    # 2) Fetch LTP for RELIANCE (token "2885")
    ltp_resp = client.ltpData("NSE", "2885")
    if ltp_resp.get("status") and ltp_resp.get("data"):
        ltp = ltp_resp["data"].get("ltp")
        send_telegram(f"📈 RELIANCE LTP: ₹{ltp}")
    else:
        send_telegram(f"❌ LTP fetch failed:\n```{ltp_resp}```")

if __name__ == "__main__":
    main()
