from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "8116462125:AAF-Nw313C1vew8Y96InHWJBXX9VnwbxFFc"
CHAT_ID = "665594180"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

@app.route("/", methods=["GET"])
def home():
    return "✅ TradingView Webhook Bot is live!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received:", data)

    # Extract message from alert
    message = data.get("message", "⚠️ Alert received but no 'message' field found.")
    send_telegram_message(f"📈 TradingView Alert:\n\n{message}")
    
    return {"status": "success"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
