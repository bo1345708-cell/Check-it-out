import os
import time
import requests
import telebot
from flask import Flask

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"
# တိုက်ရိုက် API လင့်ခ်အသစ်သို့ ပြောင်းလဲခြင်း
API_URL = "https://hongguoduanju.com/api/index/category?time=1&sort_type=1"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    print("🎬 API မှတစ်ဆင့် ရုပ်ရှင်အသစ်များကို စစ်ဆေးနေပါသည်...", flush=True)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://hongguoduanju.com/",
            "Accept": "application/json, text/plain, */*"
        }
        
        response = requests.get(API_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API ဒေတာ အောင်မြင်စွာ ရရှိပါပြီ...", flush=True)
            
            # API မှ ရလာမည့် JSON စာရင်းထဲမှ ပထမဆုံး ရုပ်ရှင်အသစ်ကို ထုတ်ယူခြင်း
            book_list = data.get('data', {}).get('bookList', []) or data.get('book_list', []) or data.get('list', [])
            
            if not book_list and isinstance(data.get('data'), list):
                book_list = data.get('data')

            if book_list and len(book_list) > 0:
                latest_book = book_list[0]
                latest_movie = latest_book.get('book_name', '') or latest_book.get('name', '') or latest_book.get('title', '')
                image_url = latest_book.get('thumb_url', '') or latest_book.get('cover_url', '') or latest_book.get('pic_url', '')
                
                if latest_movie != last_saved_movie and latest_movie != "":
                    caption = f"🎬 ရုပ်ရှင်အသစ်တင်ပါပြီ!\n\nခေါင်းစဉ်: {latest_movie}\nလင့်ခ်: https://hongguoduanju.com/"
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
            else:
                print("⚠️ API ထဲတွင် ရုပ်ရှင်စာရင်း မတွေ့ရသေးပါ။", flush=True)
        else:
            print(f"❌ API ချိတ်ဆက်၍မရပါ (Status: {response.status_code})", flush=True)
    except Exception as e:
        print(f"❌ Error ဖြစ်နေပါသည်: {e}", flush=True)

@app.route('/')
def home():
    check_new_movie()
    return "Movie Monitor API Bot is Active!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
