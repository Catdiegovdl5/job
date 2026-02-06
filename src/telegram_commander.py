import logging
import os
import subprocess
import sys
import shutil
import re
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

    if data.startswith("approve_bid|"):
        job_title = data.split("|")[1]
        await query.edit_message_text(text=f"✅ Aprovado! Iniciando lance para: {job_title}")

        move_proposal_file(job_title, "approved")
        trigger_bidder(job_title)

    elif data.startswith("reject_bid|"):
        job_title = data.split("|")[1]
        await query.edit_message_text(text=f"❌ Rejeitado: {job_title}")

        move_proposal_file(job_title, "rejected")

def move_proposal_file(job_title, status):
    # Sanitize title to match filename generation logic
    safe_title = re.sub(r'[\\/*?:"<>|]', "", job_title).replace(" ", "_")
    filename = f"WAITING_APPROVAL_{safe_title}.txt"

    base_dir = "propostas_geradas"
    source = os.path.join(base_dir, filename)

    if status == "approved":
        dest_dir = os.path.join(base_dir, "processadas")
    else:
        dest_dir = os.path.join(base_dir, "descartadas")

    if os.path.exists(source):
        try:
            # Ensure dest dir exists (created in setup but good to check)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(source, os.path.join(dest_dir, filename))
            print(f"File moved to {dest_dir}: {filename}")
        except Exception as e:
            print(f"Error moving file: {e}")
    else:
        print(f"File not found for moving: {source}")

def trigger_bidder(job_title):
    print(f"[Commander] Triggering Bidder for {job_title}")
    # Construct subprocess call to src/bidder.py
    user = os.getenv("FLN_USER") or os.getenv("FREELANCER_EMAIL") or "unknown"
    password = os.getenv("FLN_PASS") or os.getenv("FREELANCER_PASSWORD") or "unknown"

    script_path = os.path.join(os.path.dirname(__file__), "bidder.py")

    try:
        subprocess.Popen([
            sys.executable,
            script_path,
            "--user", user,
            "--password", password,
            "--url", job_title
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
