import os
import time
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import subprocess
import sys
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv("src/.env")

# Configuration
WATCH_DIR = "propostas_geradas"
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# State
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

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        keyboard = [
            [
                InlineKeyboardButton("✅ Sim, enviar", callback_data=f"send_{f}"),
                InlineKeyboardButton("❌ Editar", callback_data=f"edit_{f}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await context.bot.send_message(chat_id=CHAT_ID, text=f"📜 **Nova Proposta Gerada**\n\n{content[:3000]}", parse_mode="Markdown", reply_markup=reply_markup)

            new_path = filepath.replace("WAITING_APPROVAL_", "PENDING_DECISION_")
            os.rename(filepath, new_path)

        except Exception as e:
            print(f"[ERROR] Telegram send failed: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, filename = data.split("_", 1)

    pending_path = os.path.join(WATCH_DIR, f"PENDING_DECISION_{filename}")

    if not os.path.exists(pending_path):
        await query.edit_message_text(text="⚠️ Arquivo não encontrado ou já processado.")
        return

    if action == "send":
        await query.edit_message_text(text=f"🚀 Iniciando Bidder para {filename}...")

        final_path = os.path.join(WATCH_DIR, f"SUBMITTED_{filename}")
        os.rename(pending_path, final_path)

        # Read content to find URL
        url = None
        proposal_body = ""
        with open(final_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract URL from header line "URL: ..."
            url_match = re.search(r"URL: (http[s]?://\S+)", content)
            if url_match:
                url = url_match.group(1).strip()

            parts = content.split("---", 2)
            if len(parts) > 2:
                proposal_body = parts[2].strip() # Content after header
            else:
                proposal_body = content # Fallback

        if url:
            subprocess.Popen([sys.executable, "src/bidder.py", url, proposal_body])
        else:
            await context.bot.send_message(chat_id=CHAT_ID, text="⚠️ Erro: URL não encontrada no arquivo da proposta.")

    elif action == "edit":
        user_states[query.from_user.id] = {'file': pending_path, 'state': 'EDITING'}
        await query.edit_message_text(text="✏️ Modo de Edição Ativo. Envie o novo texto da proposta:")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_states and user_states[user_id]['state'] == 'EDITING':
        state = user_states[user_id]
        filepath = state['file']
        new_text = update.message.text

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_text)

        del user_states[user_id]

        keyboard = [
            [
                InlineKeyboardButton("✅ Sim, enviar agora", callback_data=f"send_{os.path.basename(filepath).replace('PENDING_DECISION_', '')}"),
                InlineKeyboardButton("❌ Editar novamente", callback_data=f"edit_{os.path.basename(filepath).replace('PENDING_DECISION_', '')}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"📝 **Proposta Atualizada**\n\n{new_text[:3000]}", parse_mode="Markdown", reply_markup=reply_markup)

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("[CRITICAL] TELEGRAM_TOKEN or TELEGRAM_CHAT_ID missing. Commander cannot start.")
        sys.exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    job_queue = app.job_queue
    job_queue.run_repeating(check_files, interval=10, first=5)

    print("🤖 Commander Listening...")
    app.run_polling()
