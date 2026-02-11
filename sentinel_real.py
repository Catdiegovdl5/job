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
# Note: Keeping GROQ_KEY variable for compatibility if needed elsewhere, but using GEMINI_API_KEY for proposal generation
GROQ_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
API_SECRET = os.environ.get("API_SECRET", "1234")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# Thread Safety
memory_lock = threading.Lock()
MEMORY_FILE = "memory.json"

def load_memory():
    with memory_lock:
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    data = json.load(f)
                    # Initialize default mission if missing
                    if "current_mission" not in data:
                        data["current_mission"] = "python automation scraping"
                    return data
            except: pass
        return {"current_mission": "python automation scraping"}

def save_memory(data):
    with memory_lock:
        try:
            with open(MEMORY_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")

memory = load_memory()

def gerar_proposta_groq(titulo, desc):
    # INTEGRATION DIEGO (GEMINI) - Maintaining function name for compatibility
    if not GEMINI_API_KEY: return "⚠️ Configure GEMINI_API_KEY."

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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'candidates' in data and data['candidates']:
            texto_final = data['candidates'][0]['content']['parts'][0]['text']

            # --- LIMPEZA BRUTA DE SÍMBOLOS (SAFETY NET) ---
            texto_final = texto_final.replace("**", "")
            texto_final = texto_final.replace("##", "")
            texto_final = texto_final.replace("###", "")
            texto_final = texto_final.replace("|", "")
            texto_final = texto_final.replace("---", "")
            texto_final = texto_final.replace("Subject:", "")
            texto_final = texto_final.replace("[Client Name]", "")

            # FILTRO DE HIGIENIZAÇÃO RESTAURADO (OBRIGATÓRIO)
            texto_final = texto_final.replace("Jules", "Diego")
            texto_final = texto_final.replace("Dear Client,", "")
            texto_final = texto_final.replace("I'm excited to bid", "I analyzed your requirements")

            return texto_final.strip()
        else:
            return f"Error: No candidates returned from API. Response: {json.dumps(data)}"
    except Exception as e:
        return f"Erro Gemini: {str(e)}"

def criar_painel_controle(project_id, link):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Ver no Site", url=link))
    btn_approve = InlineKeyboardButton("✅ Aprovar", callback_data=f"approve_{project_id}")
    btn_reject = InlineKeyboardButton("❌ Ignorar", callback_data=f"ignore_{project_id}")
    markup.row(btn_approve, btn_reject)
    return markup

def scan_radar():
    # Use lock only for reading configuration to minimize lock time
    current_query = ""
    with memory_lock:
        if not bot or not FLN_TOKEN: return
        current_query = memory.get("current_mission", "python automation scraping")

    logger.info("📡 Varredura V17 iniciada...")

    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=current_query, search_filter=search_filter)

        if result and 'projects' in result:
            for p in result['projects'][:2]:
                pid = str(p.get('id'))
                if p.get('budget', {}).get('minimum', 0) < 15: continue

                # Check memory safely
                is_known = False
                with memory_lock:
                    if pid in memory: is_known = True

                if is_known: continue

                title = p.get('title')
                link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"

                # Gera proposta com a nova função blindada
                texto = gerar_proposta_groq(title, p.get('preview_description', ''))

                msg1 = bot.send_message(CHAT_ID, f"🎯 *ALVO NA MIRA*\n\n📝 {title}\n💰 {p.get('budget', {}).get('minimum')} USD", parse_mode="Markdown", reply_markup=criar_painel_controle(pid, link))
                msg2 = bot.send_message(CHAT_ID, f"```\n{texto}\n```", parse_mode="Markdown")

                # Update memory safely
                with memory_lock:
                    memory[pid] = {'alert_id': msg1.message_id, 'prop_id': msg2.message_id}
                    try:
                        with open(MEMORY_FILE, "w") as f:
                            json.dump(memory, f)
                    except Exception as e:
                        logger.error(f"Erro ao salvar memória: {e}")

                time.sleep(5)
    except Exception as e:
        logger.error(f"Erro: {e}")

if bot:
    @bot.message_handler(commands=['menu'])
    def menu_command(message):
        markup = InlineKeyboardMarkup()
        btn_python = InlineKeyboardButton("🐍 Python Elite", callback_data="set_python")
        btn_quick = InlineKeyboardButton("⚡ Caixa Rápido", callback_data="set_quick")
        btn_web = InlineKeyboardButton("🌐 Web Dev", callback_data="set_web")
        markup.add(btn_python)
        markup.add(btn_quick)
        markup.add(btn_web)
        bot.send_message(message.chat.id, "🛠 *Painel de Controle Tático*\nEscolha o Tipo de Missão:", parse_mode="Markdown", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        try:
            # Mission Selection Handlers
            if call.data.startswith("set_"):
                new_mission = ""
                mission_name = ""

                if call.data == "set_python":
                    new_mission = "python automation scraping"
                    mission_name = "🐍 Python Elite"
                elif call.data == "set_quick":
                    new_mission = "scraping data entry excel vba script"
                    mission_name = "⚡ Caixa Rápido"
                elif call.data == "set_web":
                    new_mission = "website react wordpress nodejs"
                    mission_name = "🌐 Web Dev"

                if new_mission:
                    with memory_lock:
                        memory["current_mission"] = new_mission
                        try:
                            with open(MEMORY_FILE, "w") as f:
                                json.dump(memory, f)
                        except Exception as e:
                            logger.error(f"Erro ao salvar memória: {e}")

                    bot.answer_callback_query(call.id, f"Modo: {mission_name}")
                    bot.send_message(call.message.chat.id, f"✅ *Modo Alterado para: {mission_name}*", parse_mode="Markdown")

            elif "_" in call.data:
                # BLINDAGEM DO SPLIT
                action, pid = call.data.split("_", 1)

                if action == "approve":
                    bot.answer_callback_query(call.id, "✅ Aprovado!")
                    bot.edit_message_text(f"✅ *APROVADO*\nID: {pid}", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
                elif action == "ignore":
                    bot.answer_callback_query(call.id, "❌ Limpando...")

                    ids = None
                    with memory_lock:
                        ids = memory.get(pid)

                    if ids:
                        try: bot.delete_message(chat_id=call.message.chat.id, message_id=ids['alert_id'])
                        except: pass
                        try: bot.delete_message(chat_id=call.message.chat.id, message_id=ids['prop_id'])
                        except: pass

                        with memory_lock:
                            if pid in memory:
                                del memory[pid]
                                try:
                                    with open(MEMORY_FILE, "w") as f:
                                        json.dump(memory, f)
                                except Exception as e:
                                    logger.error(f"Erro ao salvar memória: {e}")
        except Exception as e:
            logger.error(f"Erro no callback: {e}")

def monitor():
    while True:
        scan_radar()
        # ACELERAR RADAR (3 MINUTOS)
        time.sleep(180)

class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Mantém o Health Check para o Render não matar o bot
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ONLINE - API READY")
    def do_POST(self):
        # Verifica a senha do Gem
        auth_header = self.headers.get('X-Api-Key')
        if auth_header != API_SECRET:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
            return

        # Rota: Alterar Modo de Missão
        if self.path == "/api/set_mode":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            try:
                data = json.loads(post_body)
                new_mode = data.get("mode")

                # Mapa de Modos
                mission_map = {
                    "python": "python automation scraping",
                    "quick": "scraping data entry excel vba script",
                    "web": "website react wordpress nodejs"
                }

                if new_mode in mission_map:
                    with memory_lock:
                        memory["current_mission"] = mission_map[new_mode]
                        try:
                            with open(MEMORY_FILE, "w") as f:
                                json.dump(memory, f)
                        except Exception as e:
                            logger.error(f"Erro ao salvar memória: {e}")

                    # Feedback no Log e Telegram
                    logger.info(f"API: Modo alterado para {new_mode}")
                    if bot:
                        bot.send_message(CHAT_ID, f"📡 *Comando Remoto Recebido*\nModo ativado: `{new_mode.upper()}`", parse_mode="Markdown")
                        # Ping de Confirmação
                        bot.send_message(CHAT_ID, f"📡 [COMANDO OPAL] - Modo alterado para: {new_mode.upper()}")

                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success", "mode": new_mode}).encode())
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Invalid mode")
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid JSON")
            except Exception as e:
                logger.error(f"API Error: {e}")
                self.send_response(500)
                self.end_headers()

        # Rota: Status Report
        elif self.path == "/api/status":
            self.send_response(200)
            self.end_headers()

            status_data = {}
            with memory_lock:
                status_data = {
                    "online": True,
                    "current_mission": memory.get("current_mission"),
                    "projects_processed": len(memory)
                }

            self.wfile.write(json.dumps(status_data).encode())

PORT = int(os.environ.get("PORT", 10000))

if __name__ == "__main__":
    logger.info("🔒 Thread Lock ativado. Memória protegida.")
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), APIHandler).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor, daemon=True).start()
    if bot:
        logger.info("🤖 Jules V17 (Diego Edition) ONLINE")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
