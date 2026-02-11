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
    # IMPLEMENTAÇÃO BLINDADA "DIEGO"
    if not GROQ_KEY: return "⚠️ Configure GROQ_API_KEY."

    prompt = f"""
    ### SYSTEM OVERRIDE: PROTOCOLO SNIPER V2 ###
    ROLE: You are NOT a freelancer. You are 'Diego', an Elite Python Automation Architect & Growth Hacker charging $150/hr. You close deals by exposing flaws in the client's request using Reverse Engineering.

    ### THE "ANTI-FLUFF" DIRECTIVE (STRICT):
    1. NO greetings ("Hello", "Dear", "Hi"). Start with the DIAGNOSIS.
    2. NO generic claims ("I have experience", "I can do this"). SHOW, don't tell.
    3. NO placeholders ([X], [Date]). Use "TBD" or "Negotiable".
    4. MAX LENGTH: 1200 chars. Concise & Brutal.

    ### YOUR ARSENAL (SELECT ONLY RELEVANT TOOLS):
    [IF SCRAPING/BOTS]: Use "Headless Browsers", "Anti-Detect Fingerprinting", "Dockerized Microservices", "Redis Queue".
    [IF WEB/APP]: Use "React/Next.js", "Server-Side Rendering (SEO)", "Supabase", "Clean Architecture".
    [IF DATA/MARKETING]: Use "CAPI (Conversions API)", "GTM Server-Side", "Snowflake", "Python Pandas".
    [IF AI/LLM]: Use "RAG Pipeline", "Vector Database", "Fine-Tuning Llama-3", "LangChain".

    ### EXECUTION STRUCTURE (MANDATORY MARKDOWN):
    1. **The Diagnosis:** Identify the hidden risk or bottleneck in their description immediately. (e.g., "Your current approach will get blocked by Cloudflare...").
    2. **The Blueprint (Table):**
       | Phase | Technical Action | Business Impact (ROI) |
       |-------|------------------|-----------------------|
       | 1 | [Specific Tech] | [Specific Outcome] |
       | 2 | [Specific Tech] | [Specific Outcome] |
    3. **Why This Stack:** Briefly explain the selected Arsenal tools (max 2 lines).
    4. **The Challenge (CTA):** "I have a Docker container ready to test this. Are you available for a 5-min demo?"

    ### INPUT DATA:
    Project: '{titulo}'
    Description: {desc}

    >>> GENERATE PROPOSAL NOW (SIGN AS 'DIEGO'):
    """
    try:
        # Usando biblioteca oficial Groq ou Requests direto para Llama-3
        # Adaptando para a biblioteca 'groq' que já estava instalada
        client = Groq(api_key=GROQ_KEY)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        texto_final = completion.choices[0].message.content

        # FILTRO DE HIGIENIZAÇÃO (Trava de Segurança)
        texto_final = texto_final.replace("Jules", "Diego")
        texto_final = texto_final.replace("Dear Client,", "")
        texto_final = texto_final.replace("I'm excited to bid", "I analyzed your requirements")
        texto_final = texto_final.replace("[X]", "negotiable")

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
