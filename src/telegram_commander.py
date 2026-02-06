import logging
import os
import subprocess
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sniper Engine Online. Awaiting alerts.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Systems Nominal. Sniper Mode Active.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("send_bid|"):
        job_title = data.split("|")[1]
        await query.edit_message_text(text=f"✅ Iniciando lance para: {job_title}")

        # Trigger Bidder
        trigger_bidder(job_title)

    elif data == "ignore_bid":
        await query.edit_message_text(text="❌ Vaga ignorada.")

def trigger_bidder(job_title):
    print(f"[Commander] Triggering Bidder for {job_title}")
    # Construct subprocess call to src/bidder.py
    # Note: Using job_title as URL placeholder since we mocked it. In prod, pass URL.
    user = os.getenv("FLN_USER") or os.getenv("FREELANCER_EMAIL") or "unknown"
    password = os.getenv("FLN_PASS") or os.getenv("FREELANCER_PASSWORD") or "unknown"

    script_path = os.path.join(os.path.dirname(__file__), "bidder.py")

    try:
        subprocess.Popen([
            sys.executable,
            script_path,
            "--user", user,
            "--password", password,
            "--url", job_title # Passing title as mock URL
        ])
    except Exception as e:
        print(f"Error launching bidder: {e}")

def run_bot():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN not found in .env")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Telegram Bot Polling Started...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()
