import os
import time
import json
import re
import requests
import telebot
from flask import Flask

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"
# တိုက်ရိုက် အလုပ်လုပ်မည့် ပင်မဝဘ်ဆိုဒ်လင့်ခ်
TARGET_URL = "https://hongguoduanju.com/"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    print("🎬 Hongguo ဝဘ်ဆိုဒ်မှ အချက်အလက်များကို စစ်ဆေးနေပါသည်...", flush=True)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://hongguoduanju.com/"
        }
        
        # Requests ဖြင့် ပင်မစာမျက်နှာကို ခေါ်ယူခြင်း
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Next.js ၏ JSON Data ကို ရှာဖွေခြင်း
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
            if match:
                print("✅ ပင်မ JSON Data ကို အောင်မြင်စွာ ရရှိပါပြီ...", flush=True)
                json_raw = match.group(1)
                
                # နာမည်နှင့် ပုံများကို Regex ဖြင့် အလွယ်တကူ ရှာဖွေထုတ်ယူခြင်း
                titles = re.findall(r'"(book_name|name|title)":"([^"]+)"', json_raw)
                images = re.findall(r'"(thumb_url|cover_url|pic_url)":"([^"]+)"', json_raw)
                
                if titles:
                    # ပထမဆုံး တွေ့ရသည့် ရုပ်ရှင်အသစ်ကို ယူမည်
                    latest_movie = titles[0][1].encode('utf-8').decode('unicode_escape').strip()
                    image_url = images[0][1].encode('utf-8').decode('unicode_escape').strip() if images else ""
                    
                    if latest_movie != last_saved_movie and latest_movie != "":
                        caption = f"🎬 ရုပ်ရှင်အသစ်တင်ပါပြီ!\n\nခေါင်းစဉ်: {latest_movie}\nလင့်ခ်: {TARGET_URL}"
                        try:
                            if image_url:
                                if not image_url.startswith('http'):
                                    image_url = "https:" + image_url if image_url.startswith('//') else TARGET_URL + image_url
                                img_response = requests.get(image_url, headers=headers, timeout=10)
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
                    print("⚠️ JSON ထဲတွင် ရုပ်ရှင်ခေါင်းစဉ် မတွေ့ရပါ။", flush=True)
            else:
                print("❌ __NEXT_DATA__ ကို ရှာမတွေ့ပါ။ Cloudflare က Page အပြည့်အစုံ မပေးသေးပါ။", flush=True)
        else:
            print(f"❌ ဝဘ်ဆိုဒ်သို့ ချိတ်ဆက်၍မရပါ (Status: {response.status_code})", flush=True)
    except Exception as e:
        print(f"❌ Error ဖြစ်နေပါသည်: {e}", flush=True)

@app.route('/')
def home():
    check_new_movie()
    return "Movie Monitor Bot is Ready and Working!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
