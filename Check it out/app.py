import os
import time
import json
import re
import cloudscraper
import requests
import telebot
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

# Telegram Bot Token နှင့် Chat ID
BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"
TARGET_URL = "https://hongguoduanju.com/category?time=1&sort_type=1"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
scraper = cloudscraper.create_scraper() # Cloudflare ကျော်ရန် 

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    try:
        response = scraper.get(TARGET_URL)
        html_content = response.text
        
        # Next.js Data ထဲမှ JSON ကို ရှာခြင်း
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if match:
            json_data = json.loads(match.group(1))
            
            # JSON ဖွဲ့စည်းပုံအရ ခေါင်းစဉ်နှင့် ပုံကို ရှာခြင်း (Regex ဖြင့် အလွယ်ရှာခြင်း)
            title_match = re.search(r'"(book_name|name|title)":"([^"]+)"', match.group(1))
            img_match = re.search(r'"(thumb_url|cover_url|pic_url)":"([^"]+)"', match.group(1))
            
            if title_match:
                latest_movie = title_match.group(2).strip()
                latest_movie = latest_movie.encode('utf-8').decode('unicode_escape') # တရုတ်စာလုံး အမှန်ပေါ်ရန်
                
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
                    print(f"Sent notification for: {latest_movie}")
                else:
                    print("No new movie yet.")
    except Exception as e:
        print(f"Error checking movie: {e}")

# Render မအိပ်သွားစေရန် Self-pinging ပြုလုပ်ခြင်း
def ping_self():
    try:
        # သင်၏ Render Web Service URL ကို ဤနေရာတွင် ပြောင်းထည့်ရန်လိုနိုင်သည်
        url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:10000')
        requests.get(url)
    except:
        pass

# Web Server Route (Render အတွက် လိုအပ်သည်)
@app.route('/')
def keep_alive():
    return "Movie Monitor Bot is Running!"

if __name__ == "__main__":
    # ၁၀ မိနစ်တစ်ကြိမ် Movie စစ်ဆေးရန်နှင့် ၅ မိနစ်တစ်ကြိမ် Ping ရန် Schedule ဆွဲခြင်း
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_new_movie, trigger="interval", minutes=10)
    scheduler.add_job(func=ping_self, trigger="interval", minutes=5)
    scheduler.start()
    
    # ချက်ချင်းတစ်ခါ အရင်စစ်ဆေးရန်
    check_new_movie()
    
    # Render ၏ Port အတိုင်း Flask ကို Run ပါ
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)