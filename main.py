from flask import Flask, request
import requests
import gspread
from google.oauth2 import service_account
from datetime import datetime
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

app = Flask(__name__)

# Telegram setup
BOT_TOKEN = "8116462125:AAF-Nw313C1vew8Y96InHWJBXX9VnwbxFFc"
CHAT_ID = "665594180"

# Google Sheets setup
SHEET_ID = "1FBdmLVH2_m823pSfA3xyOCNEvimSSO7ebvYbDXCd2-0"
SHEET_NAME = "Sheet1"

# Google Auth from env
def get_google_creds():
    credentials_dict = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI")
    }
    return service_account.Credentials.from_service_account_info(credentials_dict)

def append_to_google_sheet(message):
    try:
        creds = get_google_creds()
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([timestamp, message])
    except Exception as e:
        print("Google Sheets error:", e)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

@app.route("/")
def home():
    return "✅ TradingView Telegram + Sheets bot is live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", "⚠️ No 'message' in alert")

    send_telegram_message(f"📈 TradingView Alert:\n\n{message}")
    append_to_google_sheet(message)

    return {"status": "success"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
