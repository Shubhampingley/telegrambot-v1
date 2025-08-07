import os
import json
import requests
from SmartApi.smartConnect import SmartConnect

# Environment variables
API_KEY = os.getenv("ANGEL_API_KEY")
ACCESS_TOKEN = os.getenv("ANGEL_ACCESS_TOKEN")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Mapping of stock symbols to their NSE token IDs
symbol_token_map = {
    "RELIANCE": "2885",
    "TCS": "11536"
    # Add more symbols and their NSE token IDs here
}

# Initialize Angel One client
obj = SmartConnect(api_key=API_KEY)
obj.setAccessToken(ACCESS_TOKEN)

# Function to fetch LTP
def get_ltp(symbol):
    try:
        params = {
            "exchange": "NSE",
            "tradingsymbol": symbol,
            "symboltoken": symbol_token_map[symbol]
        }

        response = obj.get_ltp_data(params)

        if not response or "data" not in response:
            return "Error: Invalid response"

        if response.get("status") != "success":
            return f"Error: {response.get('message', 'status')}"

        ltp = response["data"]["ltp"]
        return f"₹{ltp}"

    except Exception as e:
        return f"Error: {str(e)}"

# Prepare message
def prepare_message(symbols):
    message = "📊 *LTP Update:*\n"
    for symbol in symbols:
        ltp = get_ltp(symbol)
        message += f"• {symbol}: {ltp}\n"
    return message

# Send Telegram message
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print("❌ Failed to send Telegram message")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# Main script
if __name__ == "__main__":
    stock_list = ["RELIANCE", "TCS"]  # Add more as needed
    message = prepare_message(stock_list)
    send_telegram_message(message)
