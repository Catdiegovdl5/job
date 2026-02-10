import time
import logging
import os
import threading
import http.server
import socketserver
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV16")

# Credenciais
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Memória temporária
propostas_cache = {}

def gerar_proposta_groq(titulo, desc):
    if not client: return "⚠️ Configure GROQ_API_KEY."
    try:
        # PROMPT OTIMIZADO V16
        prompt = (
            f"Write a professional, persuasive bid for project: '{titulo}'. "
            f"Description: {desc}. "
            "Constraints: "
            "1. Output ONLY the bid body. "
            "2. Start with 'Dear Client,'. "
            "3. Keep it under 1500 characters. "
            "4. NEVER use placeholders like '[X]' or brackets. "
            "5. If budget/timeline is unknown, use generic phrases like 'negotiable' or 'to be discussed'. "
            "Sign as 'Jules'."
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
    logger.info("📡 Varredura V16 (Texto Curto) iniciada...")
    
    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        query = "python automation scraping"
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=query, search_filter=search_filter)
        
        if result and 'projects' in result:
            for p in result['projects'][:2]:
                pid = p.get('id')
                if p.get('budget', {}).get('minimum', 0) < 15: continue
                
                title = p.get('title')
                desc = p.get('preview_description', '')
                link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"
                
                # Gera proposta
                texto_proposta = gerar_proposta_groq(title, desc)
                
                msg = (
                    f"🎯 *ALVO NA MIRA*\n\n"
                    f"📝 *Projeto:* {title}\n"
                    f"💰 *Valor:* {p.get('budget', {}).get('minimum')} USD\n\n"
                    f"👇 *Escolha uma ação:*"
                )
                
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=criar_painel_controle(pid, link))
                bot.send_message(CHAT_ID, f"```\n{texto_proposta}\n```", parse_mode="Markdown")
                
                time.sleep(5) 
                
    except Exception as e:
        logger.error(f"❌ Erro no Radar: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        if "_" not in call.data: return
        action, pid = call.data.split("_")
        
        if action == "approve":
            bot.answer_callback_query(call.id, "✅ Copie o texto abaixo e envie!")
            bot.edit_message_text(f"✅ *APROVADO*\n(Copie a proposta abaixo e envie)", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
            
        elif action == "ignore":
            bot.answer_callback_query(call.id, "❌ Descartado")
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            
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
        logger.info("🤖 Jules V16 ONLINE")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
