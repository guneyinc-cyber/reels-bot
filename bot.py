import os
import telebot
import requests
from flask import Flask, request

# --- KİŞİSEL BİLGİLERİN ---
TOKEN = "8797134611:AAF7qbv62oVaAGdVrk-ZTh8qB8a2nYYeYc4"
MY_ID = 5563898074
RENDER_URL = "https://reels-bot-hhhk.onrender.com"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

def get_video_data(url):
    # Stabil çalışan indirme servisi
    api_url = f"https://api.snapinsta.workers.dev/?url={url}"
    try:
        r = requests.get(api_url, timeout=10).json()
        if r['status'] == 'success' and len(r['data']) > 0:
            return r['data'][0]['url'], r['data'][0]['title']
    except Exception as e:
        print(f"API Hatası: {e}")
    return None, None

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == MY_ID:
        bot.reply_to(message, "Hoş geldin! Reels linkini gönder, senin için indireyim.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id != MY_ID:
        return
    
    if "instagram.com/" in message.text:
        wait_msg = bot.reply_to(message, "⏳ Video analiz ediliyor, lütfen bekleyin...")
        video_url, title = get_video_data(message.text)
        
        if video_url:
            try:
                bot.send_video(message.chat.id, video_url, caption=title)
                bot.delete_message(message.chat.id, wait_msg.message_id)
            except Exception as e:
                bot.edit_message_text(f"⚠️ Video gönderilemedi: {e}", message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Video bulunamadı. Linkin herkese açık olduğundan emin olun.", message.chat.id, wait_msg.message_id)
    else:
        bot.reply_to(message, "Lütfen geçerli bir Instagram Reels linki gönder.")

# Webhook Yönlendirmesi
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    return "Bot Aktif ve Bağlantı Hazır!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
