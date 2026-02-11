import time
import logging
import os
import threading
import http.server
import socketserver
import json
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV17")

# Credenciais
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# Client Groq mantido para compatibilidade, mas usaremos requests para controle total se preferir,
# ou a biblioteca oficial. Aqui ajustado para usar a lógica blindada.
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {}

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Erro ao salvar memória: {e}")

memory = load_memory()

def gerar_proposta_groq(titulo, desc):
    # IMPLEMENTAÇÃO "DIEGO" - V4 PLAIN TEXT (ZERO FORMATTING)
    if not GROQ_KEY: return "⚠️ Configure GROQ_API_KEY."

    prompt = f"""
    ### SYSTEM OVERRIDE: PROTOCOLO HUMANO PURO (NO MARKDOWN) ###

    **ROLE:** You are 'Diego', an Elite Solutions Architect. You are writing a quick, direct message to a client.

    **CRITICAL FORMATTING RULES (STRICT):**
    1. **ABSOLUTELY NO MARKDOWN:** Do NOT use asterisks (**bold**), underscores (_italic_), or hash signs (#).
    2. **NO TABLES:** Do NOT use pipes (|) or dashes (---).
    3. **NO BULLET POINTS:** Do NOT use lists with *. Use numbers (1.) or just line breaks.
    4. **PLAIN TEXT ONLY:** Use only letters, numbers, commas, and periods.

    **TONE:** - Conversational, professional, slightly informal (like a senior expert).
    - No "Sales" fluff.

    **STRUCTURE:**
    1. **The Hook:** Start directly discussing their technical problem (e.g., "I saw your project regarding Loterias...").
    2. **The Plan:** List 3 steps using this format: "Phase 1: Action - Outcome".
    3. **The Stack:** One sentence on why you chose the tools.
    4. **The Close:** Ask for a 5-min demo.

    ### INPUT DATA:
    Project: '{titulo}'
    Description: {desc}

    >>> WRITE THE PROPOSAL NOW (PLAIN TEXT ONLY, NO SYMBOLS):
    """
    try:
        client = Groq(api_key=GROQ_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        texto_final = completion.choices[0].message.content

        # --- LIMPEZA BRUTA DE SÍMBOLOS (SAFETY NET) ---
        # Remove qualquer vestígio de Markdown que a IA teimar em colocar
        texto_final = texto_final.replace("**", "")
        texto_final = texto_final.replace("##", "")
        texto_final = texto_final.replace("###", "")
        texto_final = texto_final.replace("|", "")
        texto_final = texto_final.replace("---", "")
        texto_final = texto_final.replace("Subject:", "")
        texto_final = texto_final.replace("[Client Name]", "")

        return texto_final.strip()
    except Exception as e:
        return f"Erro Groq: {e}"

def criar_painel_controle(project_id, link):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Ver no Site", url=link))
    btn_approve = InlineKeyboardButton("✅ Aprovar", callback_data=f"approve_{project_id}")
    btn_reject = InlineKeyboardButton("❌ Ignorar", callback_data=f"ignore_{project_id}")
    markup.row(btn_approve, btn_reject)
    return markup

def scan_radar():
    if not bot or not FLN_TOKEN: return
    logger.info("📡 Varredura V17 iniciada...")
    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        query = "python automation scraping"
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=query, search_filter=search_filter)

        if result and 'projects' in result:
            for p in result['projects'][:2]:
                pid = str(p.get('id'))
                if p.get('budget', {}).get('minimum', 0) < 15: continue
                if pid in memory: continue
                title = p.get('title')
                link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"

                # Gera proposta com a nova função blindada
                texto = gerar_proposta_groq(title, p.get('preview_description', ''))

                msg1 = bot.send_message(CHAT_ID, f"🎯 *ALVO NA MIRA*\n\n📝 {title}\n💰 {p.get('budget', {}).get('minimum')} USD", parse_mode="Markdown", reply_markup=criar_painel_controle(pid, link))
                msg2 = bot.send_message(CHAT_ID, f"```\n{texto}\n```", parse_mode="Markdown")

                memory[pid] = {'alert_id': msg1.message_id, 'prop_id': msg2.message_id}
                save_memory(memory)
                time.sleep(5)
    except Exception as e:
        logger.error(f"Erro: {e}")

if bot:
    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        try:
            if "_" not in call.data: return
            action, pid = call.data.split("_")

            if action == "approve":
                bot.answer_callback_query(call.id, "✅ Aprovado!")
                bot.edit_message_text(f"✅ *APROVADO*\nID: {pid}", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
            elif action == "ignore":
                bot.answer_callback_query(call.id, "❌ Limpando...")
                ids = memory.get(pid)
                if ids:
                    try: bot.delete_message(chat_id=call.message.chat.id, message_id=ids['alert_id'])
                    except: pass
                    try: bot.delete_message(chat_id=call.message.chat.id, message_id=ids['prop_id'])
                    except: pass
                    del memory[pid]
                    save_memory(memory)
        except: pass

def monitor():
    while True:
        scan_radar()
        time.sleep(900)

PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor, daemon=True).start()
    if bot:
        logger.info("🤖 Jules V17 (Diego Edition) ONLINE")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
