import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sniper Engine Online. Awaiting commands.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Systems Nominal. Sniper Mode Active.")

def run_bot():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN not found in .env")
        return

    # FIX: ApplicationBuilder automatically handles JobQueue in v20+
    # Ensure we use the builder pattern which is standard for modern python-telegram-bot
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    status_handler = CommandHandler('status', status)

    application.add_handler(start_handler)
    application.add_handler(status_handler)

    print("Telegram Bot Polling Started...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()
