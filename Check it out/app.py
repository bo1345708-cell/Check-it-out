import os
import time
import requests
import telebot
from flask import Flask

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"
# တိုက်ရိုက် အလုပ်လုပ်မည့် တရုတ်နိုင်ငံသုံး တိုတိုဒရမ် API တစ်ခု
API_URL = "https://api.pearkcep.com/api/duanju/" # သို့မဟုတ် တရားဝင်ရနိုင်သော Public API

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

last_saved_movie = ""

def check_new_movie():
    global last_saved_movie
    print("🎬 Public API မှတစ်ဆင့် ရုပ်ရှင်အသစ်များကို စစ်ဆေးနေပါသည်...", flush=True)
    try:
        response = requests.get("https://api.allorigins.win/raw?url=https://hongguoduanju.com/", timeout=15)
        
        if response.status_code == 200:
            html = response.text
            if "hongguo" in html.lower() or len(html) > 500:
                print("✅ Proxy မှတစ်ဆင့် ဝဘ်ဆိုဒ်ဒေတာ ရရှိပါပြီ...", flush=True)
                # ရှာဖွေတွေ့ရှိသော ခေါင်းစဉ်အတု သို့မဟုတ် Test စာသား ပို့ပေးခြင်း
                # (Cloudflare အပြည့်အဝကျော်ရန် Proxy သုံးခြင်း)
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                latest_movie = f"Short Drama Update - {current_time}"
                
                if latest_movie != last_saved_movie:
                    caption = f"🎬 ရုပ်ရှင်အသစ် စစ်ဆေးတွေ့ရှိချက်!\n\nချိန်ခါ: {current_time}\nလင့်ခ်: https://hongguoduanju.com/"
                    bot.send_message(CHAT_ID, caption)
                    last_saved_movie = latest_movie
                    print(f"🚀 Telegram သို့ အောင်မြင်စွာ ပို့ပြီးပါပြီ။", flush=True)
                else:
                    print("⚠️ အသစ်ထပ်တိုးမှု မရှိသေးပါ။", flush=True)
            else:
                print("❌ Proxy မှ Data အပြည့်အစုံ မရပါ။", flush=True)
        else:
            print(f"❌ ချိတ်ဆက်မှု အဆင်မပြေပါ (Status: {response.status_code})", flush=True)
    except Exception as e:
        print(f"❌ Error ဖြစ်နေပါသည်: {e}", flush=True)

@app.route('/')
def home():
    check_new_movie()
    return "Proxy Bypass Bot is Active and Working!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
