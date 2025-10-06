import os
import telebot
import datetime as dt
import pytz
from flask import Flask
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Берём токен и chat_id из переменных окружения Render
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)
# --- запустить приём апдейтов Телеграм в фоне ---
import threading
def _start_polling():
    bot.infinity_polling(timeout=60, long_polling_timeout=50)

threading.Thread(target=_start_polling, daemon=True).start()
# --- конец блока ---

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

# ===== === AI-помощник в боте ===== ===

def ai_answer(text: str) -> str:
    """
    Короткий, деловой ответ на русском.
    """
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # быстрый и бесплатный в Groq
            messages=[
                {"role": "system", "content": "Отвечай кратко и по делу на русском языке."},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Ошибка AI: {e}"

@bot.message_handler(commands=['ai', 'ask'])
def ai_handler(message):
    """
    Использование:
    /ai ТЗ для ответа
    /ask вопрос
    Если текста нет — подставит шаблон.
    """
    parts = message.text.split(maxsplit=1)
    user_text = parts[1].strip() if len(parts) > 1 else "Сделай план на неделю по ИИ-обучению для предпринимателя."

    bot.send_chat_action(message.chat.id, 'typing')
    try:
        answer = ai_answer(user_text)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка AI: {e}")
