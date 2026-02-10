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
logger = logging.getLogger("JulesV14")

# Credenciais
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

def gerar_proposta_groq(titulo, desc):
    if not client: return "⚠️ Configure a GROQ_API_KEY no Render."
    try:
        # Prompt ajustado para ser DIRETO (sem enrolação)
        prompt = (
            f"Act as a top-tier freelancer. Write a professional, persuasive bid for this project: '{titulo}'. "
            f"Description: {desc}. "
            "Output ONLY the bid text. Do not write 'Here is the bid'. Start with 'Dear Client,' or similar. "
            "Sign as 'Jules'."
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro Groq: {e}"

def criar_botao(link):
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton("🔗 Ver no Site", url=link)
    markup.add(btn)
    return markup

def scan_radar():
    if not bot or not FLN_TOKEN: return
    logger.info("📡 Varredura V14 (Botões Ativos) iniciada...")

    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        query = "python automation scraping"
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=query, search_filter=search_filter)

        if result and 'projects' in result:
            for p in result['projects'][:2]:
                # Filtro de orçamento ($15+)
                if p.get('budget', {}).get('minimum', 0) < 15: continue

                title = p.get('title')
                desc = p.get('preview_description', '')
                link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"

                # Gera proposta
                proposta = gerar_proposta_groq(title, desc)

                # Monta a mensagem
                msg = (
                    f"🚀 *ALVO DETECTADO*\n\n"
                    f"📝 *Projeto:* {title}\n"
                    f"💰 *Valor:* {p.get('budget', {}).get('minimum')} USD\n\n"
                    f"⚡ *PROPOSTA GROQ:*\n```\n{proposta}\n```"
                )

                # Envia COM O BOTÃO (AQUI ESTÁ A CORREÇÃO)
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=criar_botao(link))
                time.sleep(5)

    except Exception as e:
        logger.error(f"❌ Erro no Radar: {e}")

def monitor():
    while True:
        scan_radar()
        logger.info("💤 Dormindo 15min...")
        time.sleep(900)

# Servidor para manter o Render vivo
PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor, daemon=True).start()

    if bot:
        logger.info("🤖 Jules V14 ONLINE")
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Erro Polling: {e}")
            time.sleep(5)
