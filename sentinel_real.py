import time
import logging
import os
import threading
import http.server
import socketserver
import telebot
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("JulesV17")

# Credenciais
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# RASTREADOR DE MENSAGENS (Para apagar o par: Botão + Texto)
# Formato: {"project_id": [msg_id_painel, msg_id_texto]}
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar memory.json: {e}")
    return {}

def save_memory():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(message_tracker, f)
    except Exception as e:
        logger.error(f"Erro ao salvar memory.json: {e}")

message_tracker = load_memory()

def gerar_proposta_groq(titulo, desc):
    if not client: return "⚠️ Configure GROQ_API_KEY."
    try:
        # Prompt V16 (Otimizado: Curto e sem placeholders)
        prompt = (
            f"Write a technical, direct bid as Diego. Max 1500 chars. No intro, no fluff. Start with \"Hello,\". Focus on Python/Scraping. Sign ONLY as \"Diego\". NEVER use [X]. "
            f"Project: \"{titulo}\". Description: {desc}."
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
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
    logger.info("📡 Varredura V17 (Limpeza Automática) iniciada...")
    
    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        query = "python automation scraping"
        search_filter = create_search_projects_filter(sort_field="time_updated", project_types=["fixed"])
        result = search_projects(session, query=query, search_filter=search_filter)
        
        if result and "projects" in result:
            for p in result["projects"][:2]:
                pid = str(p.get("id"))
                
                # Evita duplicar se já processamos (opcional, mas bom pra evitar spam)
                if pid in message_tracker: continue

                if p.get("budget", {}).get("minimum", 0) < 15: continue
                
                title = p.get("title")
                desc = p.get("preview_description", "")
                link = f"https://www.freelancer.com/projects/{p.get("seo_url")}"
                
                texto_proposta = gerar_proposta_groq(title, desc)
                
                msg_painel_texto = (
                    f"🎯 *ALVO NA MIRA*\\n\\n"
                    f"📝 *Projeto:* {title}\\n"
                    f"💰 *Valor:* {p.get("budget", {}).get("minimum")} USD\\n\\n"
                    f"👇 *Escolha uma ação:*"
                )
                
                # 1. Envia Painel e guarda o objeto da mensagem
                sent_painel = bot.send_message(CHAT_ID, msg_painel_texto, parse_mode="Markdown", reply_markup=criar_painel_controle(pid, link))
                
                # 2. Envia Proposta e guarda o objeto da mensagem
                sent_proposta = bot.send_message(CHAT_ID, f"```\\n{texto_proposta}\\n```", parse_mode="Markdown")
                
                # 3. Salva os DOIS IDs no rastreador
                message_tracker[pid] = [sent_painel.message_id, sent_proposta.message_id]
                save_memory()
                
                time.sleep(5) 
                
    except Exception as e:
        logger.error(f"❌ Erro no Radar: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        if "_" not in call.data: return
        action, pid = call.data.split("_")
        
        if action == "approve":
            bot.answer_callback_query(call.id, "✅ Aprovado! Copie o texto abaixo.")
            # Edita o painel para mostrar que foi aprovado
            bot.edit_message_text(
                f"✅ *APROVADO*\\nProjeto ID: {pid}\\n(Texto disponível abaixo)",
                chat_id=call.message.chat.id, 
                message_id=call.message.message_id, 
                parse_mode="Markdown"
            )
            # Removemos do rastreador para não apagar mais tarde sem querer
            if pid in message_tracker:
                del message_tracker[pid]
                save_memory()
            
        elif action == "ignore":
            bot.answer_callback_query(call.id, "❌ Apagando tudo...")
            
            # Lógica de Limpeza Dupla
            if pid in message_tracker:
                msg_ids = message_tracker[pid]
                for mid in msg_ids:
                    try:
                        bot.delete_message(chat_id=call.message.chat.id, message_id=mid)
                    except Exception as e:
                        logger.error(f"Erro ao apagar msg {mid}: {e}")
                # Remove da memória
                del message_tracker[pid]
                save_memory()
            else:
                # Fallback: Se o bot reiniciou e perdeu a memória, apaga pelo menos o botão
                try:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                except: pass
            
    except Exception as e:
        logger.error(f"Erro botão: {e}")

def monitor():
    while True:
        scan_radar()
        logger.info("💤 Dormindo 15min...")
        time.sleep(900)

PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor, daemon=True).start()
    if bot:
        logger.info("🤖 Jules V17 ONLINE")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
