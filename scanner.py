import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ─── Configuration ──────────────────────────────────────────────────────────────
API_KEY     = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
M_PIN       = os.getenv("ANGEL_PASSWORD")    # your M-PIN
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TG_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

# ─── Telegram helper ─────────────────────────────────────────────────────────────
def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, data=payload)
        print("Telegram status:", resp.status_code)
    except Exception:
        pass

# ─── Main ────────────────────────────────────────────────────────────────────────
def main():
    # 1) Login & grab tokens
    client = SmartConnect(api_key=API_KEY)
    totp   = pyotp.TOTP(TOTP_SECRET).now()
    resp   = client.generateSession(
        clientCode=CLIENT_CODE,
        password=M_PIN,
        totp=totp
    )

    data       = resp.get("data") or {}
    refresh    = data.get("refreshToken")
    feed_token = data.get("feedToken")

    if not refresh or not feed_token:
        send_telegram(f"❌ Login failed – response:\n```{resp}```")
        return

    # 2) Set tokens for subsequent calls
    client.setAccessToken(refresh)    # use refreshToken here
    client.setFeedToken(feed_token)

    # 3) Fetch LTP for RELIANCE (token=2885)
    ltp_resp = client.ltpData("NSE", "RELIANCE", "2885")
    if ltp_resp.get("status") and ltp_resp.get("data"):
        price = ltp_resp["data"]["ltp"]
        send_telegram(f"📈 *RELIANCE LTP:* ₹{price}")
    else:
        send_telegram(f"❌ LTP fetch failed:\n```{ltp_resp}```")

if __name__ == "__main__":
    main()
