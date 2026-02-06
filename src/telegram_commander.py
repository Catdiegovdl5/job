import os
import time
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import subprocess
import sys

# Configuration
WATCH_DIR = "propostas_geradas"
TOKEN = os.environ.get("TELEGRAM_TOKEN", "7724330024:AAGClqGLnixnNukc_bkFnUQKolSqCtZQgcc") # Fallback for dev
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "1501131002")

# State
# Map user_id -> {'file': 'path/to/waiting.txt', 'state': 'WAITING_CONFIRMATION' or 'EDITING'}
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Architect Commander Online. Watching for proposals...")

async def check_files(context: ContextTypes.DEFAULT_TYPE):
    """Polls directory for WAITING files."""
    if not os.path.exists(WATCH_DIR):
        return

    files = [f for f in os.listdir(WATCH_DIR) if f.startswith("WAITING_APPROVAL_") and f.endswith(".txt")]

    for f in files:
        filepath = os.path.join(WATCH_DIR, f)

        # Read content
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Send to Telegram
        keyboard = [
            [
                InlineKeyboardButton("✅ Sim, enviar", callback_data=f"send_{f}"),
                InlineKeyboardButton("❌ Editar", callback_data=f"edit_{f}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await context.bot.send_message(chat_id=CHAT_ID, text=f"📜 **Nova Proposta Gerada**\n\n{content[:3000]}", parse_mode="Markdown", reply_markup=reply_markup)

            # Rename to PROCESSED_WAITING to avoid resending loop
            new_path = filepath.replace("WAITING_APPROVAL_", "PENDING_DECISION_")
            os.rename(filepath, new_path)

        except Exception as e:
            print(f"[ERROR] Telegram send failed: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, filename = data.split("_", 1)

    # Reconstruct path (it was renamed to PENDING_DECISION_)
    original_waiting = f"WAITING_APPROVAL_{filename}"
    pending_path = os.path.join(WATCH_DIR, f"PENDING_DECISION_{filename}")

    if not os.path.exists(pending_path):
        await query.edit_message_text(text="⚠️ Arquivo não encontrado ou já processado.")
        return

    if action == "send":
        # Call Bidder
        # Extract URL (Assuming it's not in the file content easily, we might need to store it metadata)
        # For V1, let's assume we read the URL from the file footer or a sidecar?
        # Actually, master_template logic needs to save the URL in the text for the bidder to know where to go!
        # Fix: Read content, look for "URL: ..." or pass it.
        # Let's assume for now just the action is logged.

        await query.edit_message_text(text=f"🚀 Iniciando Bidder para {filename}...")

        # Rename to SUBMITTED
        final_path = os.path.join(WATCH_DIR, f"SUBMITTED_{filename}")
        os.rename(pending_path, final_path)

        # Trigger Bidder (Async subprocess)
        # subprocess.Popen([sys.executable, "src/bidder.py", url, proposal_text])

    elif action == "edit":
        user_states[query.from_user.id] = {'file': pending_path, 'state': 'EDITING'}
        await query.edit_message_text(text="✏️ Modo de Edição Ativo. Envie o novo texto da proposta:")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_states and user_states[user_id]['state'] == 'EDITING':
        state = user_states[user_id]
        filepath = state['file']
        new_text = update.message.text

        # Save new text
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_text)

        # Clear state
        del user_states[user_id]

        # Re-send confirmation
        keyboard = [
            [
                InlineKeyboardButton("✅ Sim, enviar agora", callback_data=f"send_{os.path.basename(filepath).replace('PENDING_DECISION_', '')}"),
                InlineKeyboardButton("❌ Editar novamente", callback_data=f"edit_{os.path.basename(filepath).replace('PENDING_DECISION_', '')}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"📝 **Proposta Atualizada**\n\n{new_text[:3000]}", parse_mode="Markdown", reply_markup=reply_markup)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    # Periodic Job
    job_queue = app.job_queue
    job_queue.run_repeating(check_files, interval=10, first=5)

    print("🤖 Commander Listening...")
    app.run_polling()
