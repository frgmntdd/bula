import telebot
import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# --- НАСТРОЙКИ И ИНИЦИАЛИЗАЦИЯ ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("TELEGRAM_TOKEN и GEMINI_API_KEY должны быть установлены в переменных окружения.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
# Используем надежную и мощную модель
model = genai.GenerativeModel('gemini-1.5-pro-latest')

print("Бот запущен и готов к работе...") # Сообщение, которое мы увидим в логах Render

# --- ОСНОВНАЯ ЛОГИКА БОТА ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Приветствую. BOT DEVELOPED AND POWERED BY BULLS")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    placeholder = None
    try:
        placeholder = bot.reply_to(message, "⏳ Думаю над вашим запросом...")

        # Делаем запрос к Gemini без тайм-аута, т.к. Render нам это позволяет
        response = model.generate_content(message.text)

        bot.edit_message_text(
            chat_id=placeholder.chat.id,
            message_id=placeholder.message_id,
            text=response.text
        )
    except Exception as e:
        print(f"[ERROR] Произошла ошибка: {e}")
        if placeholder:
            bot.edit_message_text(
                chat_id=placeholder.chat.id,
                message_id=placeholder.message_id,
                text=f"😥 **Произошла ошибка.**\n\nТехническая информация:\n`{e}`"
            )

# --- ЗАПУСК БОТА В РЕЖИМЕ ПОЛЛИНГА ---
# Эта строка заставляет бота постоянно опрашивать сервера Telegram на наличие новых сообщений.
# Это идеальный режим для всегда включенных серверов, как Render.
if __name__ == "__main__":
    bot.infinity_polling()