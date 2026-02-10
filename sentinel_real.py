import time
import logging
import os
import threading
import http.server
import socketserver
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

# --- CONFIGURAÇÃO BÁSICA ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV12")

# --- CHAVES ---
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# --- FUNÇÃO PARA CRIAR BOTÕES ---
def criar_botoes(link, projeto_id):
    markup = InlineKeyboardMarkup()
    # Botão 1: Link Direto
    btn_link = InlineKeyboardButton("🔗 Ver no Freelancer", url=link)
    # Botão 2: Callback para pedir o Prompt
    btn_prompt = InlineKeyboardButton("🤖 Gerar Prompt IA", callback_data=f"prompt_{projeto_id}")
    
    markup.add(btn_link)
    markup.add(btn_prompt)
    return markup

# --- A MENTE DO ROBÔ (V12 - COM DETALHES) ---
def scan_fast_cash():
    if not bot or not FLN_TOKEN: return

    logger.info("📡 Varredura V12 (Com Botões) iniciada...")
    
    # Lista de Nichos
    search_queries = [
        "python automation scraping", 
        "market research competitor", 
        "video creation tiktok ai"
    ]

    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        
        for query in search_queries:
            search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
            result = search_projects(session, query=query, search_filter=search_filter)

            if result and 'projects' in result:
                for p in result['projects'][:3]: 
                    
                    # Filtros Básicos
                    budget = p.get('budget', {})
                    min_b = budget.get('minimum')
                    curr = p.get('currency', {}).get('code', 'UNK')

                    if min_b is None or min_b < 15: continue
                    if curr not in ['USD', 'EUR', 'GBP', 'AUD', 'CAD']: continue 

                    # Dados do Projeto
                    pid = p.get('id')
                    title = p.get('title')
                    link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"
                    # PEGAR A DESCRIÇÃO (NOVO!)
                    desc = p.get('preview_description', 'Sem descrição disponível.')[:200] + "..." 

                    # Monta a mensagem bonita
                    msg = (
                        f"🚀 *NOVO ALVO DETECTADO*\n\n"
                        f"📂 *Nicho:* {query}\n"
                        f"📝 *Projeto:* {title}\n"
                        f"💰 *Valor:* {min_b} {curr}\n\n"
                        f"📄 *Resumo:* _{desc}_\n"
                    )

                    # Envia com Botões
                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=criar_botoes(link, pid))
                    time.sleep(2) 
            
            time.sleep(1)

    except Exception as e:
        logger.error(f"❌ Erro: {e}")

# --- REAÇÃO AOS BOTÕES (CALLBACK) ---
if bot:
    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        # Se o usuário clicar em "Gerar Prompt IA"
        if call.data.startswith("prompt_"):
            bot.answer_callback_query(call.id, "Gerando prompt...")
            msg_prompt = (
                "📋 *COPIE E COLE NO GEMINI/VEO:*\n\n"
                "```\n"
                "Atue como um Especialista Sênior. Analise este projeto freelancer:\n"
                "[Cole a descrição do projeto aqui]\n\n"
                "1. Crie uma proposta irrecusável em Inglês.\n"
                "2. Liste o passo a passo técnico para resolver.\n"
                "3. Estime o prazo real."
                "\n```"
            )
            bot.send_message(call.message.chat.id, msg_prompt, parse_mode="Markdown")

def monitor_loop():
    while True:
        scan_fast_cash()
        logger.info("💤 Dormindo 15min...")
        time.sleep(900)

# --- SERVER ---
PORT = int(os.environ.get("PORT", 10000))
class Health(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ONLINE")

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Health).serve_forever(), daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()
    if bot: bot.infinity_polling()
