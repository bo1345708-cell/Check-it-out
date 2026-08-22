import os
import time
import requests
import telebot
from flask import Flask

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    print("🎬 ရုပ်ရှင်အသစ်များကို စစ်ဆေးနေပါသည်...", flush=True)
    try:
        # ရိုးရှင်းပြီး အမြန်ဆုံး အလုပ်လုပ်မည့် တရုတ်နိုင်ငံသုံး ဒရမ် အချက်အလက် API အစားထိုးခြင်း
        api_url = "https://api.pearkcep.com/api/duanju/"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API ဒေတာ ရရှိပါပြီ...", flush=True)
            
            # ဒေတာထဲမှ ရုပ်ရှင်နာမည်ကို ထုတ်ယူခြင်း
            if "data" in data and data["data"]:
                movie_name = data["data"].get("title", "Chinese Short Drama")
                
                if movie_name != last_saved_movie:
                    caption = f"🎬 ရုပ်ရှင်အသစ်တင်ပါပြီ!\n\nခေါင်းစဉ်: {movie_name}\nလင့်ခ်: https://hongguoduanju.com/"
                    bot.send_message(CHAT_ID, caption)
                    last_saved_movie = movie_name
                    print(f"🚀 Telegram သို့ ပို့ပြီးပါပြီ: {movie_name}", flush=True)
                else:
                    print("⚠️ အသစ်ထပ်တိုးမှု မရှိသေးပါ။", flush=True)
            else:
                print("⚠️ API ထဲတွင် ဒေတာ အလွတ်ဖြစ်နေပါသည်။", flush=True)
        else:
            print(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ (Status: {response.status_code})", flush=True)
    except Exception as e:
        print(f"❌ Error ဖြစ်နေပါသည်: {e}", flush=True)

@app.route('/')
def home():
    check_new_movie()
    return "Stable Monitor Bot is Active!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
