import os
import telebot
import datetime as dt
import pytz
from flask import Flask

# Берём токен и chat_id из переменных окружения Render
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

TZ = pytz.timezone("Asia/Novosibirsk")  # Кемерово

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я буду напоминать по воскресеньям в 12:00 (Кемерово). Команды: /ping, /plan")

# Проверка живости
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "pong ✅")

# Отправка плана
@bot.message_handler(commands=['plan'])
def plan(message):
    bot.reply_to(message, "Напоминание: подготовить план на неделю!")

# Flask endpoint для Render
@server.route("/")
def webhook():
    now = dt.datetime.now(TZ)
    if now.weekday() == 6 and now.hour == 12 and now.minute < 5:  # Воскресенье 12:00-12:05
        bot.send_message(CHAT_ID, "⏰ Воскресенье! Время составить план на неделю.")
    return "Bot is running"

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
