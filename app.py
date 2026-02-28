import os
import json
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# -------------------------
# Telegram Ayarları
# -------------------------
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

# -------------------------
# Dosya / Duplicate Kontrol
# -------------------------
ILAN_DOSYA = "ilanlar.json"
if not os.path.exists(ILAN_DOSYA):
    with open(ILAN_DOSYA, "w", encoding="utf-8") as f:
        json.dump([], f)

with open(ILAN_DOSYA, "r", encoding="utf-8") as f:
    onceki = json.load(f)

tum_ilanlar = []

# -------------------------
# Güvenli Request Fonksiyonu
# -------------------------
def safe_request(url, method="GET", json_payload=None):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        if method.upper() == "POST":
            return requests.post(url, headers=headers, json=json_payload, timeout=15)
        return requests.get(url, headers=headers, timeout=15)
    except:
        return None

# -------------------------
# 1️⃣ İŞKUR
# -------------------------
def iskur():
    url = "https://esube.iskur.gov.tr/Istihdam/JobList"
    r = safe_request(url)
    if not r:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        link = a.get("href")
        if text and link and len(text) > 15:
            if not link.startswith("http"):
                link = "https://esube.iskur.gov.tr" + link
            ilanlar.append((text, link, "İŞKUR"))
    return ilanlar

# -------------------------
# 2️⃣ ilan.gov.tr
# -------------------------
def ilan_gov():
    url = "https://www.ilan.gov.tr/ilan/kategori/8/kamu-akademik-personel"
    r = safe_request(url)
    if not r:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        link = a.get("href")
        if text and link and "ilan" in link:
            if not link.startswith("http"):
                link = "https://www.ilan.gov.tr" + link
            ilanlar.append((text, link, "ilan.gov.tr"))
    return ilanlar

# -------------------------
# 3️⃣ Resmi Gazete
# -------------------------
def resmi_gazete():
    url = "https://www.resmigazete.gov.tr/"
    r = safe_request(url)
    if not r:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    ilanlar = []
    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        link = a.get("href")
        if text and "personel" in text.lower():
            ilanlar.append((text, link, "Resmi Gazete"))
    return ilanlar

# -------------------------
# 4️⃣ SBB Kamuilan (JSON endpoint)
# -------------------------
def sbb_json():
    url = "https://kamuilan.sbb.gov.tr/api/v1/jobs"
    r = safe_request(url)
    if not r:
        return []
    try:
        data = r.json()
        ilanlar = []
        for item in data.get("jobs", []):
            baslik = item.get("title", "")
            link = "https://kamuilan.sbb.gov.tr" + item.get("detailUrl", "")
            ilanlar.append((baslik, link, "SBB Kamuilan"))
        return ilanlar
    except:
        return []

# -------------------------
# 5️⃣ Kariyer Kapısı (JSON endpoint)
# -------------------------
def kariyer_json():
    url = "https://kariyerkapisi.gov.tr/api/jobs/search"
    payload = {
        "page": 1,
        "size": 50,
        "filters": {"isPublic": True}
    }
    r = safe_request(url, method="POST", json_payload=payload)
    if not r:
        return []
    try:
        data = r.json()
        ilanlar = []
        for item in data.get("data", []):
            baslik = item.get("title", "")
            link = "https://kariyerkapisi.gov.tr" + item.get("url", "")
            ilanlar.append((baslik, link, "Kariyer Kapısı"))
        return ilanlar
    except:
        return []

# -------------------------
# TÜM SİTELERİ ÇEK
# -------------------------
for site in [iskur, ilan_gov, resmi_gazete, sbb_json, kariyer_json]:
    try:
        tum_ilanlar += site()
    except:
        continue

# -------------------------
# FİLTRELE
# -------------------------
yeni = []

for baslik, link, kaynak in tum_ilanlar:
    key = baslik + link
    if key in onceki:
        continue

    if any(x in baslik for x in ["KPSS", "Memur", "Daimi", "Kamu"]):
        yeni.append((baslik, link, kaynak))
        onceki.append(key)

# -------------------------
# TELEGRAM GÖNDER
# -------------------------
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


from telegram import Bot
import os
import asyncio

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

async def test_mesaj():
    await bot.send_message(chat_id=CHAT_ID, text="🚨 Bu bir test mesajıdır!")

asyncio.run(test_mesaj())
