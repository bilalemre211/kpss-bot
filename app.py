# app.py
import os
import json
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Telegram bilgileri
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise ValueError("⚠ TOKEN veya CHAT_ID eksik!")

bot = Bot(token=TOKEN)

# İlanlar dosyası
ILAN_DOSYA = "ilanlar.json"

# Dosya yoksa oluştur
if not os.path.exists(ILAN_DOSYA):
    with open(ILAN_DOSYA, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# İlanları dosyadan oku
with open(ILAN_DOSYA, "r", encoding="utf-8") as f:
    onceki_ilanlar = json.load(f)

# İŞKUR URL (örnek)
URL = "https://esube.iskur.gov.tr/Istihdam/JobList"

# Web sitesinden ilanları çek
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

# Tüm ilan başlıkları
tum_ilanlar = []
for ilan in soup.find_all("div", class_="job-title"):  # siteye göre class değişebilir
    text = ilan.get_text(strip=True)
    tum_ilanlar.append(text)

# Sadece yeni ilanları filtrele
yeni_ilanlar = []
for ilan in tum_ilanlar:
    if ilan in onceki_ilanlar:
        continue
    # KPSS’li ilan
    if "KPSS" in ilan:
        yeni_ilanlar.append(ilan)
    # KPSS’siz memur / daimi / kamu ilanı
    elif any(x in ilan for x in ["Memur", "Daimi", "Kamu"]) and "KPSS" not in ilan:
        yeni_ilanlar.append(ilan)

# Yeni ilan varsa Telegram’a gönder
async def gonder():
    for ilan in yeni_ilanlar:
        await bot.send_message(chat_id=CHAT_ID, text=f"🚨 Yeni İlan: {ilan}")

if yeni_ilanlar:
    asyncio.run(gonder())

# Son durumları kaydet
with open(ILAN_DOSYA, "w", encoding="utf-8") as f:
    json.dump(tum_ilanlar, f, ensure_ascii=False, indent=2)

print(f"{len(yeni_ilanlar)} yeni ilan kontrol edildi ve gönderildi.")
