import os
import telebot
import requests
import re
from flask import Flask, request

TOKEN = "8797134611:AAF7qbv62oVaAGdVrk-ZTh8qB8a2nYYeYc4"
MY_ID = 5563898074
RENDER_URL = "https://reels-bot-hhhk.onrender.com"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

def get_reels_video(url):
    # Bu servis şu an Instagram'ın en güncel engellerini aşabiliyor
    api_url = "https://worker-crimson-sun-2983.arif-helmi.workers.dev/"
    payload = {"url": url}
    
    try:
        # Tarayıcı gibi görünmek için sahte başlıklar ekliyoruz
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        r = requests.post(api_url, json=payload, headers=headers, timeout=15).json()
        
        # Servis yanıtını kontrol et
        if 'url' in r:
            return r['url'], r.get('title', 'Reels Videosu')
        elif 'data' in r and len(r['data']) > 0:
            return r['data'][0]['url'], r['data'][0].get('title', 'Reels Videosu')
    except Exception as e:
        print(f"Hata detayı: {e}")
    
    return None, None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id != MY_ID: return
    
    if "instagram.com/" in message.text:
        # Linki temizleyelim (query parametrelerini silelim)
        clean_url = message.text.split("?")[0]
        
        wait_msg = bot.reply_to(message, "⏳ Instagram engelleri aşılıyor, lütfen bekleyin...")
        
        video_url, title = get_reels_video(clean_url)
        
        if video_url:
            try:
                bot.send_video(message.chat.id, video_url, caption=title)
                bot.delete_message(message.chat.id, wait_msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"⚠️ Video bulundu ama gönderilemedi (Boyut hatası olabilir).", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Instagram bu botun erişimini şu an kısıtlıyor. Lütfen 5 dakika sonra başka bir linkle tekrar dene.", message.chat.id, wait_msg.message_id)

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    return "Bot Gelişmiş Modda Aktif!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
