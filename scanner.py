from nsetools import Nse
import requests

# Setup
nse = Nse()
TELEGRAM_BOT_TOKEN = '8116462125:AAF-Nw313C1vew8Y96InHWJBXX9VnwbxFFc'
TELEGRAM_CHAT_ID = '665594180'

# Sample stock list (you can add more)
stock_list = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK']

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)

for stock in stock_list:
    try:
        quote = nse.get_quote(stock)
        price = quote['lastPrice']
        if price and price > 2500:
            send_telegram_message(f"📈 {stock} price is ₹{price} — above ₹2500!")
    except Exception as e:
        print(f"Error with {stock}: {e}")
