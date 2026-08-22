import os
import time
import json
import re
import requests
import telebot
from flask import Flask

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"
TARGET_URL = "https://hongguoduanju.com/category?time=1&sort_type=1"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    print("🎬 Website ကို Cloudflare ကျော်ပြီး စစ်ဆေးနေပါသည်...", flush=True)
    try:
        # Cloudflare ကို ကျော်လွှားရန် နှာခေါင်းစည်း (Headers) အပြည့်အစုံဖြင့် တောင်းဆိုခြင်း
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://hongguoduanju.com/",
            "Connection": "keep-alive"
        }
        
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        html_content = response.text
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if match:
            print("✅ JSON Data အောင်မြင်စွာ ရရှိပါပြီ...", flush=True)
            json_data = json.loads(match.group(1))
            
            # JSON ထဲမှ ရုပ်ရှင်အချက်အလက်များကို ရှာဖွေခြင်း
            try:
                books = json_data['props']['pageProps']['initialState']['category']['bookList']
                if books and len(books) > 0:
                    latest_book = books[0]
                    latest_movie = latest_book.get('book_name', '') or latest_book.get('name', '') or latest_book.get('title', '')
                    image_url = latest_book.get('thumb_url', '') or latest_book.get('cover_url', '') or latest_book.get('pic_url', '')
                    
                    if latest_movie != last_saved_movie and latest_movie != "":
                        caption = f"🎬 ရုပ်ရှင်အသစ်တင်ပါပြီ!\n\nခေါင်းစဉ်: {latest_movie}\nလင့်ခ်: {TARGET_URL}"
                        try:
                            if image_url:
                                img_response = requests.get(image_url, headers=headers)
                                bot.send_photo(CHAT_ID, img_response.content, caption=caption)
                            else:
                                bot.send_message(CHAT_ID, caption)
                        except Exception as e:
                            bot.send_message(CHAT_ID, caption)
                            
                        last_saved_movie = latest_movie
                        print(f"🚀 Telegram သို့ ပို့ပြီးပါပြီ: {latest_movie}", flush=True)
                    else:
                        print(f"⚠️ ရုပ်ရှင်အသစ် မရှိသေးပါ။ (လက်ရှိ: {latest_movie})", flush=True)
            except Exception as inner_e:
                # အကယ်၍ JSON ဖွဲ့စည်းပုံ အနည်းငယ်ကွဲလွဲပါက Regex ဖြင့် ထပ်စစ်ရန်
                title_match = re.search(r'"(book_name|name|title)":"([^"]+)"', match.group(1))
                if title_match:
                    latest_movie = title_match.group(2).strip().encode('utf-8').decode('unicode_escape')
                    if latest_movie != last_saved_movie and latest_movie != "":
                        caption = f"🎬 ရုပ်ရှင်အသစ်တင်ပါပြီ!\n\nခေါင်းစဉ်: {latest_movie}\nလင့်ခ်: {TARGET_URL}"
                        bot.send_message(CHAT_ID, caption)
                        last_saved_movie = latest_movie
                        print(f"🚀 Telegram သို့ ပို့ပြီးပါပြီ: {latest_movie}", flush=True)
                    else:
                        print("⚠️ ရုပ်ရှင်အသစ် မရှိသေးပါ။", flush=True)
        else:
            print(f"❌ Data ဆွဲယူ၍မရပါ။ (Status: {response.status_code})", flush=True)
    except Exception as e:
        print(f"❌ Error ဖြစ်နေပါသည်: {e}", flush=True)

@app.route('/')
def home():
    check_new_movie()
    return "Movie Monitor Bot is Active and Checking!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
