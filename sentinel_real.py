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
logger = logging.getLogger("JulesV11")

# --- PEGANDO AS CHAVES DO COFRE ---
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# --- A MENTE DO ROBÔ (V11 - MULTI NICHO) ---
def scan_fast_cash():
    if not bot or not FLN_TOKEN:
        logger.error("❌ ERRO: Faltam as variáveis de ambiente!")
        return

    logger.info("📡 Varredura MULTI-NICHO iniciada...")
    
    # LISTA DE CAÇA - O Robô vai procurar tudo isso
    search_queries = [
        "python automation scraping script",  # Nicho 1: Código
        "market research competitor analysis", # Nicho 2: Pesquisa (Deep Research)
        "tiktok video content creation ai"     # Nicho 3: Vídeo (Veo)
    ]

    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        
        for query in search_queries:
            logger.info(f"🔎 Procurando por: {query}")
            
            # Filtro: Projetos FIXOS
            search_filter = create_search_projects_filter(
                sort_field='time_updated', 
                project_types=['fixed']
            )
            
            result = search_projects(session, query=query, search_filter=search_filter)

            if result and 'projects' in result:
                for p in result['projects'][:3]: # Top 3 de cada categoria
                    
                    budget_info = p.get('budget', {})
                    min_b = budget_info.get('minimum')
                    currency_info = p.get('currency', {})
                    currency_code = currency_info.get('code', 'UNK')

                    if min_b is None or min_b < 15: continue # Mínimo $15

                    # Aceita Dólar, Euro, Libra, e agora AUD e CAD
                    if currency_code not in ['USD', 'EUR', 'GBP', 'AUD', 'CAD']:
                        continue 

                    title = p.get('title')
                    link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"
                    
                    # Identifica qual IA usar na mensagem
                    ferramenta_sugerida = "🐍 Python/Jules"
                    if "market" in query: ferramenta_sugerida = "🧠 Deep Research"
                    if "video" in query: ferramenta_sugerida = "🎥 Veo/Video AI"

                    msg = (
                        f"🚀 *OPORTUNIDADE DETECTADA*\n"
                        f"🛠️ *Uso Sugerido:* {ferramenta_sugerida}\n\n"
                        f"📝 *Projeto:* {title}\n"
                        f"💵 *Pagamento:* {min_b} {currency_code}\n"
                        f"🔗 [Ver Proposta]({link})"
                    )

                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                    time.sleep(2) 
            
            time.sleep(2) # Respira entre uma busca e outra

    except Exception as e:
        logger.error(f"❌ Erro no Radar: {e}")

# --- O VIGIA (LOOP) ---
def monitor_loop():
    while True:
        scan_fast_cash()
        logger.info("💤 Dormindo por 15 minutos...")
        time.sleep(900)

# --- COMANDOS DO TELEGRAM ---
if bot:
    @bot.message_handler(commands=['status'])
    def send_status(message):
        bot.reply_to(message, "🦅 *JULES V11: ONLINE*\n✅ Modo: Caçador de Nichos\n✅ Render: Ativo", parse_mode="Markdown")

# --- O CORAÇÃO (SERVER WEB) ---
PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()
    logger.info(f"🤖 Jules V11: LIVE FIRE na porta {PORT}")
    if bot: bot.infinity_polling()
