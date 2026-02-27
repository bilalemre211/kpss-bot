import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time
from flask import Flask
import os

# Render üzerinde ENV ile koyacağız
TOKEN = os.environ.get("TOKEN")      # Telegram bot token
CHAT_ID = os.environ.get("CHAT_ID")  # Chat ID

bot = Bot(token=TOKEN)
app = Flask(__name__)

def kontrol_et():
    url = "https://www.iskur.gov.tr/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text().lower()

    if "kpss" in text or "memur" in text:
        bot.send_message(chat_id=CHAT_ID, text="🚨 Yeni KPSS veya memur ilanı olabilir! Kontrol et.")

@app.route("/")
def home():
    return "Bot aktif!"

if __name__ == "__main__":
    while True:
        kontrol_et()
        time.sleep(3600)  # 1 saatte bir kontrol