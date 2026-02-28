import os
import json
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(token=TOKEN)

ILAN_DOSYA = "ilanlar.json"

if not os.path.exists(ILAN_DOSYA):
    with open(ILAN_DOSYA, "w", encoding="utf-8") as f:
        json.dump([], f)

with open(ILAN_DOSYA, "r", encoding="utf-8") as f:
    onceki = json.load(f)

tum_ilanlar = []

# =========================
# 1️⃣ İŞKUR
# =========================
def iskur():
    url = "https://esube.iskur.gov.tr/Istihdam/JobList"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for item in soup.find_all("a"):
        text = item.get_text(strip=True)
        link = item.get("href")
        if text and link and len(text) > 10:
            ilanlar.append((text, "https://esube.iskur.gov.tr" + link, "İŞKUR"))
    return ilanlar

# =========================
# 2️⃣ ilan.gov.tr
# =========================
def ilan_gov():
    url = "https://www.ilan.gov.tr/ilan/kategori/8/kamu-akademik-personel"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for item in soup.find_all("a"):
        text = item.get_text(strip=True)
        link = item.get("href")
        if text and link and "ilan" in link:
            ilanlar.append((text, "https://www.ilan.gov.tr" + link, "ilan.gov.tr"))
    return ilanlar

# =========================
# 3️⃣ Resmi Gazete
# =========================
def resmi_gazete():
    url = "https://www.resmigazete.gov.tr/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for item in soup.find_all("a"):
        text = item.get_text(strip=True)
        link = item.get("href")
        if "personel" in text.lower():
            ilanlar.append((text, link, "Resmi Gazete"))
    return ilanlar

# =========================
# 4️⃣ SBB Kamuilan
# =========================
def sbb():
    url = "https://kamuilan.sbb.gov.tr/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for item in soup.find_all("a"):
        text = item.get_text(strip=True)
        link = item.get("href")
        if text and link and len(text) > 15:
            ilanlar.append((text, link, "SBB Kamuilan"))
    return ilanlar

# =========================
# 5️⃣ Kariyer Kapısı
# =========================
def kariyer():
    url = "https://kariyerkapisi.gov.tr/isealim"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for item in soup.find_all("a"):
        text = item.get_text(strip=True)
        link = item.get("href")
        if text and link and "isealim" in link:
            ilanlar.append((text, link, "Kariyer Kapısı"))
    return ilanlar


# Tüm siteleri çek
for site in [iskur, ilan_gov, resmi_gazete, sbb, kariyer]:
    try:
        tum_ilanlar += site()
    except:
        pass


# =========================
# Filtre
# =========================
yeni = []

for baslik, link, kaynak in tum_ilanlar:
    key = baslik + link
    if key in onceki:
        continue

    if any(x in baslik for x in ["KPSS", "Memur", "Daimi", "Kamu"]):
        yeni.append((baslik, link, kaynak))
        onceki.append(key)


# =========================
# Telegram Gönder
# =========================
async def gonder():
    for baslik, link, kaynak in yeni:
        mesaj = f"""🚨 Yeni Kamu İlanı

📌 {baslik}
🏢 Kaynak: {kaynak}
🔗 {link}
"""
        await bot.send_message(chat_id=CHAT_ID, text=mesaj)


if yeni:
    asyncio.run(gonder())

with open(ILAN_DOSYA, "w", encoding="utf-8") as f:
    json.dump(onceki, f)

print(f"{len(yeni)} yeni ilan bulundu ve gönderildi.")
