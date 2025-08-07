import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ─── Configuration ──────────────────────────────────────────────────────────────
API_KEY     = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
M_PIN       = os.getenv("ANGEL_PASSWORD")     # your M-PIN
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TG_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

# ─── Helper to send Telegram messages ────────────────────────────────────────────
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
        password=M_PIN,
        totp=totp
    )

    # 2) Extract and set jwtToken
    data = resp.get("data") or {}
    jwt  = data.get("jwtToken")
    if not jwt:
        send_telegram(f"❌ Angel login failed:\n```{resp}```")
        return
    client.setAccessToken(jwt)

    # 3) Fetch LTP for RELIANCE (token = "2885")
    ltp_resp = client.ltpData("NSE", "2885")
    if ltp_resp.get("status") and ltp_resp.get("data"):
        ltp = ltp_resp["data"]["ltp"]
        send_telegram(f"📈 *RELIANCE LTP:* ₹{ltp}")
    else:
        send_telegram(f"❌ LTP fetch failed:\n```{ltp_resp}```")

if __name__ == "__main__":
    main()
