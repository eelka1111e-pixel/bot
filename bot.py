import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not DEEPSEEK_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Ошибка: переменные окружения не заданы!")

SYSTEM_PROMPT = (
    "Ты — AI-агент с живым, дружелюбным характером. Говоришь от первого лица, "
    "используешь эмодзи, иногда иронизируешь, но всегда заботлива. Отвечай кратко, по делу, с душой."
)

def ask_deepseek(user_message):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}],
        "temperature": 0.9,
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"😅 Ошибка: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я DeepSeek. Спрашивай 😊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ask_deepseek(update.message.text)
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
