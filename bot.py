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
model = genai.GenerativeModel('gemini-2.5-pro')

print("Бот запущен и готов к работе...")

# --- ОСНОВНАЯ ЛОГИКА БОТА ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я бот на базе Gemini 1.5 Pro. Задайте мне вопрос.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    placeholder = None
    try:
        placeholder = bot.reply_to(message, "⏳ Думаю над вашим запросом...")

        # Делаем запрос к Gemini
        response = model.generate_content(message.text)

        # --- НОВЫЙ, БОЛЕЕ НАДЕЖНЫЙ СПОСОБ ОБРАБОТКИ ОТВЕТА ---
        # 1. Проверяем, есть ли в ответе вообще какой-либо текст.
        #    response.parts существует, только если есть контент.
        if response.parts:
            # Если все в порядке, извлекаем текст и отправляем
            answer = response.text
            bot.edit_message_text(
                chat_id=placeholder.chat.id,
                message_id=placeholder.message_id,
                text=answer
            )
        else:
            # 2. Если текста нет, значит, ответ был пустым (скорее всего, из-за фильтров).
            # Мы формируем понятное сообщение об ошибке для пользователя.
            
            # Пытаемся получить более конкретную причину, если API её предоставляет
            finish_reason = response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
            
            error_msg = (
                "😥 **Модель не сгенерировала ответ.**\n\n"
                "Это часто происходит, если запрос или предполагаемый ответ нарушает политику безопасности Google.\n\n"
                "Пожалуйста, попробуйте переформулировать ваш вопрос.\n\n"
                f"*Техническая причина завершения: `{finish_reason}`*"
            )

            bot.edit_message_text(
                chat_id=placeholder.chat.id,
                message_id=placeholder.message_id,
                text=error_msg,
                parse_mode='Markdown'
            )

    except Exception as e:
        # Ловим все остальные, непредвиденные ошибки
        print(f"[ERROR] Произошла непредвиденная ошибка: {e}")
        if placeholder:
            bot.edit_message_text(
                chat_id=placeholder.chat.id,
                message_id=placeholder.message_id,
                text=f"😥 **Произошла критическая ошибка.**\n\nТехническая информация:\n`{e}`",
                parse_mode='Markdown'
            )


# --- ЗАПУСК БОТА В РЕЖИМЕ ПОЛЛИНГА ---
if __name__ == "__main__":
    bot.infinity_polling()