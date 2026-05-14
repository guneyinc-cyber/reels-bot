import os
import telebot
import requests
from flask import Flask, request

# BİLGİLERİN
TOKEN = "8797134611:AAF7qbv62oVaAGdVrk-ZTh8qB8a2nYYeYc4"
MY_ID = 5563898074

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

def get_video_data(url):
    # Ücretsiz ve stabil bir API
    api_url = f"https://api.snapinsta.workers.dev/?url={url}"
    try:
        r = requests.get(api_url).json()
        if r['status'] == 'success':
            return r['data'][0]['url'], r['data'][0]['title']
    except:
        return None, None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.id != MY_ID:
        return
    
    if "instagram.com/" in message.text:
        wait_msg = bot.reply_to(message, "⏳ Video indiriliyor, kanka bekle...")
        video_url, title = get_video_data(message.text)
        
        if video_url:
            bot.send_video(message.chat.id, video_url, caption=title)
            bot.delete_message(message.chat.id, wait_msg.message_id)
        else:
            bot.edit_message_text("❌ Video bulunamadı. Linki kontrol et.", message.chat.id, wait_msg.message_id)
    else:
        bot.reply_to(message, "Kanka sadece Reels linki gönder.")

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    # BURASI ÖNEMLİ: Render linkini alınca burayı güncelleyeceğiz
    return "Bot Çalışıyor!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
