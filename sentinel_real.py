import time
import logging
import os
import threading
import http.server
import socketserver
import telebot
import google.generativeai as genai
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

# --- CONFIGURAÇÃO ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV13")

TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# Configura o Gemini (Se tiver chave)
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash') # Modelo mais rápido e barato
    except:
        model = None

def gerar_proposta_ia(titulo, desc):
    if not GEMINI_KEY or not model: return "⚠️ Configure a GEMINI_API_KEY no Render para gerar propostas."
    
    prompt = f"""
    Atue como um Freelancer Expert Top 1%.
    Escreva uma proposta curta e persuasiva (em Inglês) para este projeto:
    Projeto: {titulo}
    Descrição: {desc}
    
    A proposta deve ter:
    1. Saudação profissional.
    2. Mencionar experiência relevante.
    3. Call to Action (Chamar para o chat).
    NÃO coloque placeholders como [Your Name]. Assine como 'Jules'.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na IA: {e}"

# --- BOTÕES ---
def criar_botoes(link):
    markup = InlineKeyboardMarkup()
    btn_link = InlineKeyboardButton("🔗 Ver no Site", url=link)
    markup.add(btn_link)
    return markup

# --- RADAR ---
def scan_fast_cash():
    if not bot or not FLN_TOKEN: return

    logger.info("📡 Varredura V13 (Com IA) iniciada...")
    search_queries = ["python automation scraping", "market research competitor", "video creation tiktok ai"]

    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        
        for query in search_queries:
            # Busca projetos recentes
            search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
            result = search_projects(session, query=query, search_filter=search_filter)

            if result and 'projects' in result:
                for p in result['projects'][:2]: # Pega só os 2 mais recentes
                    
                    min_b = p.get('budget', {}).get('minimum')
                    curr = p.get('currency', {}).get('code', 'UNK')
                    
                    # Filtros de dinheiro e moeda
                    if min_b is None or min_b < 15: continue
                    if curr not in ['USD', 'EUR', 'GBP', 'AUD', 'CAD']: continue 

                    title = p.get('title')
                    # Limita a descrição para não estourar o prompt
                    desc = p.get('preview_description', '')[:400]
                    link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"

                    # 🧠 GERA A PROPOSTA AUTOMATICAMENTE
                    logger.info(f"🧠 Gerando proposta para: {title}")
                    proposta = gerar_proposta_ia(title, desc)

                    msg = (
                        f"🚀 *NOVO ALVO + PROPOSTA*\n\n"
                        f"📝 *Projeto:* {title}\n"
                        f"💰 *Valor:* {min_b} {curr}\n\n"
                        f"🤖 *PROPOSTA SUGERIDA (Copie Abaixo):*\n"
                        f"```\n{proposta}\n```"
                    )

                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=criar_botoes(link))
                    time.sleep(3) # Pausa para a IA pensar e não travar
            
            time.sleep(1)

    except Exception as e:
        logger.error(f"❌ Erro: {e}")

def monitor_loop():
    while True:
        scan_fast_cash()
        logger.info("💤 Dormindo 15min...")
        time.sleep(900)

PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()
    if bot: bot.infinity_polling()
