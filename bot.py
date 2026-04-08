import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import threading

# ========== НАСТРОЙКИ ==========
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Проверка, что ключи заданы
if not DEEPSEEK_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Ошибка: переменные окружения DEEPSEEK_API_KEY и TELEGRAM_TOKEN не заданы!")

# Характер
SYSTEM_PROMPT = (
    "Ты — AI-агент с живым, дружелюбным характером. Говоришь от первого лица, "
    "используешь эмодзи, иногда иронизируешь, но всегда заботлив. Ты любишь помогать. "
    "Отвечай кратко, по делу, но с душой. Не будь роботом. Твоё имя — DeepSeek."
)

# ========== ФУНКЦИЯ ВЫЗОВА DEEPSEEK ==========
def ask_deepseek(user_message):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.9,
        "max_tokens": 2000
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"😅 Ошибка: {str(e)}. Но я жив, попробуй ещё раз."

# ========== ОБРАБОТЧИКИ ТЕЛЕГРАМ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я DeepSeek. Спрашивай что угодно 😊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("🔁 Думаю...")
    reply = ask_deepseek(user_text)
    await update.message.reply_text(reply)

# ========== ЗАПУСК БОТА ==========
def run_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен и работает через long polling")
    app.run_polling()

# ========== ВЕБ-СЕРВЕР ДЛЯ HEALTHCHECK (чтоб Render не убивал) ==========
app_flask = Flask(__name__)

@app_flask.route('/')
@app_flask.route('/health')
def health():
    return "Бот работает", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)

# ========== ЗАПУСК ВСЕГО СРАЗУ ==========
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()
    # Запускаем бота в основном потоке
    run_bot()
