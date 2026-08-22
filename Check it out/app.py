import os
import time
import requests
import telebot
from flask import Flask

BOT_TOKEN = "8875910546:AAF2rtY20mMs4LUplnlPV8TvSYBflavis_I"
CHAT_ID = "-1004466488929"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    try:
        # Bot အလုပ်လုပ်နေကြောင်း စာတန်းကို Telegram သို့ တိုက်ရိုက်ပို့ခြင်း
        msg = "🤖 Movie Monitor Bot အလုပ်လုပ်နေပါပြီ!"
        bot.send_message(CHAT_ID, msg)
        return "Bot Status Sent Successfully!"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
