import os
import telebot
import requests
from flask import Flask, request

TOKEN = "8797134611:AAF7qbv62oVaAGdVrk-ZTh8qB8a2nYYeYc4"
MY_ID = 5563898074
RENDER_URL = "https://reels-bot-hhhk.onrender.com"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

def get_video_data(url):
    # 1. Alternatif Servis (SnapInsta Worker)
    try:
        api1 = f"https://api.snapinsta.workers.dev/?url={url}"
        r = requests.get(api1, timeout=10).json()
        if r['status'] == 'success' and r['data']:
            return r['data'][0]['url'], r['data'][0]['title']
    except:
        pass

    # 2. Alternatif Servis (TikWM - Instagram Destekli)
    try:
        api2 = "https://www.tikwm.com/api/data/universal"
        params = {"url": url}
        r = requests.get(api2, params=params, timeout=10).json()
        if r['code'] == 0:
            return r['data']['video'], r['data']['title']
    except:
        pass

    return None, None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id != MY_ID: return
    
    if "instagram.com/" in message.text:
        wait_msg = bot.reply_to(message, "⏳ Video indiriliyor (Servisler taranıyor)...")
        video_url, title = get_video_data(message.text)
        
        if video_url:
            try:
                bot.send_video(message.chat.id, video_url, caption=title)
                bot.delete_message(message.chat.id, wait_msg.message_id)
            except:
                bot.edit_message_text("⚠️ Video çok büyük, Telegram limitine takıldı.", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Video bulunamadı. Gizli bir hesap olabilir veya Instagram bu videoyu engelliyor.", message.chat.id, wait_msg.message_id)

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    return "Bot Hazır!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
