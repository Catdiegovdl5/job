import time
import logging
import os
import threading
import http.server
import socketserver
import telebot
from telebot import types
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

# --- CONFIGURAÇÃO BÁSICA ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV10")

# --- PEGANDO AS CHAVES DO COFRE ---
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# --- A MENTE DO ROBÔ ---
def scan_fast_cash():
    if not bot or not FLN_TOKEN:
        logger.error("❌ ERRO: Faltam as variáveis de ambiente (Tokens)!")
        return

    logger.info("📡 Varredura CAIXA RÁPIDO iniciada...")
    
    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        query = "python api script quick fix scraping"
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=query, search_filter=search_filter)

        if result and 'projects' in result:
            for p in result['projects'][:5]:
                budget_info = p.get('budget', {})
                min_b = budget_info.get('minimum')
                currency_info = p.get('currency', {})
                currency_code = currency_info.get('code', 'UNK')

                if min_b is None: continue
                if min_b < 20: continue

                moedas_fortes = ['USD', 'EUR', 'GBP', 'AUD', 'CAD']
                if currency_code not in moedas_fortes: continue 

                title = p.get('title')
                link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"
                
                msg = (f"💰 *ACHADO VALIOSO*\n\n📝 *Projeto:* {title}\n"
                       f"💵 *Pagamento:* {min_b} {currency_code}\n🔗 [Ver no Freelancer]({link})")

                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                time.sleep(2) 

    except Exception as e:
        logger.error(f"❌ Erro no Radar: {e}")

def monitor_loop():
    while True:
        scan_fast_cash()
        logger.info("💤 Dormindo por 15 minutos...")
        time.sleep(900)

if bot:
    @bot.message_handler(commands=['status'])
    def send_status(message):
        bot.reply_to(message, "🦅 *JULES V10: ONLINE*\n✅ Modo: Moeda Forte\n✅ Render: Ativo", parse_mode="Markdown")

PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()
    logger.info(f"🤖 Jules V10: LIVE FIRE na porta {PORT}")
    if bot: bot.infinity_polling()
