import os
import time
import re
import cloudscraper
import requests
import telebot
from flask import Flask

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"
TARGET_URL = "https://hongguoduanju.com/category?time=1&sort_type=1"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Cloudflare ၏ Anti-Bot ကို ကျော်လွှားရန် တကယ့် Chrome Browser ပုံစံ ဖန်တီးခြင်း
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    print("🎬 Cloudscraper ဖြင့် ရုပ်ရှင်အသစ်များကို စစ်ဆေးနေပါသည်...", flush=True)
    try:
        response = scraper.get(TARGET_URL, timeout=20)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Next.js ၏ JSON Data ကို ရှာဖွေခြင်း
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
            if match:
                print("✅ Cloudflare ကို ကျော်လွှားပြီး JSON Data ရရှိပါပြီ...", flush=True)
                json_raw = match.group(1)
                
                titles = re.findall(r'"(book_name|name|title)":"([^"]+)"', json_raw)
                images = re.findall(r'"(thumb_url|cover_url|pic_url)":"([^"]+)"', json_raw)
                
                if titles:
                    latest_movie = titles[0][1].encode('utf-8').decode('unicode_escape').strip()
                    image_url = images[0][1].encode('utf-8').decode('unicode_escape').strip() if images else ""
                    
                    if latest_movie != last_saved_movie and latest_movie != "":
                        caption = f"🎬 ရုပ်ရှင်အသစ်တင်ပါပြီ!\n\nခေါင်းစဉ်: {latest_movie}\nလင့်ခ်: {TARGET_URL}"
                        try:
                            if image_url:
                                if not image_url.startswith('http'):
                                    image_url = "https:" + image_url if image_url.startswith('//') else "https://hongguoduanju.com" + image_url
                                img_response = scraper.get(image_url, timeout=10)
                                bot.send_photo(CHAT_ID, img_response.content, caption=caption)
                            else:
                                bot.send_message(CHAT_ID, caption)
                        except Exception as e:
                            bot.send_message(CHAT_ID, caption)
                            
                        last_saved_movie = latest_movie
                        print(f"🚀 Telegram သို့ ပို့ပြီးပါပြီ: {latest_movie}", flush=True)
                    else:
                        print(f"⚠️ ရုပ်ရှင်အသစ် မရှိသေးပါ။ (လက်ရှိ: {latest_movie})", flush=True)
                else:
                    print("⚠️ JSON ထဲတွင် ခေါင်းစဉ် မတွေ့ရပါ။", flush=True)
            else:
                print("❌ HTML ထဲတွင် __NEXT_DATA__ ကို ရှာမတွေ့သေးပါ။", flush=True)
        else:
            print(f"❌ ဝဘ်ဆိုဒ်မှ Status Code {response.status_code} ဖြင့် တုံ့ပြန်ပါသည်။", flush=True)
    except Exception as e:
        print(f"❌ Error ဖြစ်နေပါသည်: {e}", flush=True)

@app.route('/')
def home():
    check_new_movie()
    return "Cloudscraper Bot is Active and Running!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
