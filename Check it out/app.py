import os
import time
import json
import re
import cloudscraper
import requests
import telebot
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"
TARGET_URL = "https://hongguoduanju.com/category?time=1&sort_type=1"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    print("🎬 Website ကို စတင်စစ်ဆေးနေပါသည်...", flush=True)
    try:
        response = scraper.get(TARGET_URL)
        html_content = response.text
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if match:
            print("✅ JSON Data ရှာတွေ့ပါသည်...", flush=True)
            title_match = re.search(r'"(book_name|name|title)":"([^"]+)"', match.group(1))
            img_match = re.search(r'"(thumb_url|cover_url|pic_url)":"([^"]+)"', match.group(1))
            
            if title_match:
                latest_movie = title_match.group(2).strip()
                latest_movie = latest_movie.encode('utf-8').decode('unicode_escape')
                image_url = img_match.group(2) if img_match else ""
                
                if latest_movie != last_saved_movie and latest_movie != "":
                    caption = f"🎬 ရုပ်ရှင်အသစ်တင်ပါပြီ!\n\nခေါင်းစဉ်: {latest_movie}\nလင့်ခ်: {TARGET_URL}"
                    try:
                        if image_url:
                            img_response = scraper.get(image_url)
                            bot.send_photo(CHAT_ID, img_response.content, caption=caption)
                        else:
                            bot.send_message(CHAT_ID, caption)
                    except Exception as e:
                        bot.send_message(CHAT_ID, caption)
                        
                    last_saved_movie = latest_movie
                    print(f"🚀 Telegram သို့ ပို့ပြီးပါပြီ: {latest_movie}", flush=True)
                else:
                    print("⚠️ ရုပ်ရှင်အသစ် မရှိသေးပါ။", flush=True)
        else:
            print(f"❌ Cloudflare ဖြင့် ပိတ်ခံထားရပါသည်။ (Status: {response.status_code})", flush=True)
    except Exception as e:
        print(f"❌ Error ဖြစ်နေပါသည်: {e}", flush=True)

def ping_self():
    try:
        url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:10000')
        requests.get(url)
    except:
        pass

@app.route('/')
def keep_alive():
    return "Movie Monitor Bot is Running!"

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_new_movie, trigger="interval", minutes=10)
    scheduler.add_job(func=ping_self, trigger="interval", minutes=5)
    scheduler.start()
    
    check_new_movie()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
