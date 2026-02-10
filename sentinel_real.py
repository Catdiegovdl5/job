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

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV10")

# Configuração via Environment Variables do Render
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# Radar: Modo Caixa Rápido
def scan_fast_cash():
    if not bot or not FLN_TOKEN:
        logger.error("❌ Erro: Verifique TG_TOKEN e FLN_OAUTH_TOKEN no Render!")
        return

    logger.info("📡 Varredura CAIXA RÁPIDO iniciada...")
    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        # Busca foca em projetos rápidos de fechar
        query = "python api script quick fix scraping"
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        
        result = search_projects(session, query=query, search_filter=search_filter)
        
        if result and 'projects' in result:
            projects = result['projects'][:5]
            for p in projects:
                # Filtro de Lucro: Projetos de $20 a $250 (Giro rápido)
                min_b = p.get('budget', {}).get('minimum', 0)
                if min_b < 20: continue
                
                title = p.get('title')
                link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"
                
                logger.info(f"🎯 ALVO DETECTADO: {title}")
                msg = f"💰 *OPORTUNIDADE CAIXA RÁPIDO*\n\n*Projeto:* {title}\n*Mínimo:* ${min_b}\n\n🔗 [Ver no Freelancer]({link})"
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                time.sleep(10) # Delay anti-spam
    except Exception as e:
        logger.error(f"❌ Erro no Radar: {e}")

def monitor_loop():
    while True:
        scan_fast_cash()
        logger.info("💤 Aguardando 15 minutos para nova varredura...")
        time.sleep(900)

# Comando /status robusto
if bot:
    @bot.message_handler(commands=['status'])
    def send_status(message):
        try:
            status_report = (
                "🦅 *JULES SNIPER V10: ONLINE*\n"
                "✅ *Modo:* Top & Caixa Rápido\n"
                "✅ *Radar:* Varrendo a cada 15min\n"
                "✅ *Servidor:* Render Cloud ativo"
            )
            bot.reply_to(message, status_report, parse_mode="Markdown")
            logger.info("🛰️ Status enviado via Telegram")
        except Exception as e:
            logger.error(f"⚠️ Erro no comando status: {e}")

# Servidor para o Render não derrubar o bot (Porta Dinâmica)
PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"JULES_V10_ACTIVE")

if __name__ == "__main__":
    # Inicia Servidor Web
    web_server = threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True)
    web_server.start()
    
    # Inicia Radar
    radar_thread = threading.Thread(target=monitor_loop, daemon=True)
    radar_thread.start()
    
    logger.info(f"🤖 Jules V10: LIVE FIRE MODE na porta {PORT}")
    if bot:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    else:
        while True: time.sleep(60)
