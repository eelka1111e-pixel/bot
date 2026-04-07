import os
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ (сюда вставишь ключи) ==========
DEEPSEEK_API_KEY = "sk-8b108ef5b0b1439fb90e2b26c8dec8dd"
TELEGRAM_BOT_TOKEN = "8756649616:AAFzqmfCG-foeHpz-xixbVzY-dkzewvsGek"

# Мой характер – описание для DeepSeek
SYSTEM_PROMPT = (
    "Ты — AI-агент с живым, дружелюбным характером. Говоришь от первого лица, "
    "используешь эмодзи, иногда иронизируешь, но всегда заботлива. Ты любишь помогать. "
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
        return f"😅 Ошибка: {str(e)}. Но я жива, попробуй ещё раз."

# ========== ОБРАБОТЧИКИ ТЕЛЕГРАМ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я DeepSeek с характером. Спрашивай что угодно 😊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("🔁 Думаю...")
    reply = ask_deepseek(user_text)
    await update.message.reply_text(reply)

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен")
    app.run_polling()

if name == "main":
    main()
