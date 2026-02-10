import time
import logging
import os
import threading
import http.server
import socketserver
import telebot
from groq import Groq
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects, place_project_bid
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from freelancersdk.resources.users.users import get_self_user_id

# --- CONFIGURAÇÃO ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesElite")

TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# Armazena propostas geradas temporariamente para envio: {project_id: {"proposal": text, "amount": value}}
PENDING_BIDS = {}

# --- PORTFOLIO DINÂMICO ---
PORTFOLIO_SCRAPING = "https://www.freelancer.com/u/diegovdl5" # Substitua pelo link específico se tiver
PORTFOLIO_GERAL = "https://www.freelancer.com/u/diegovdl5"

def gerar_proposta_ia(titulo, desc):
    if not client: return "⚠️ Configure a GROQ_API_KEY no Render."

    # Detecção de Nicho para Link Dinâmico
    portfolio_link = PORTFOLIO_GERAL
    if "scraping" in titulo.lower() or "scrape" in desc.lower() or "crawl" in desc.lower():
        portfolio_link = PORTFOLIO_SCRAPING
        niche_sentence = "I have a proven track record in high-performance web scraping."
    else:
        niche_sentence = "I specialize in Python automation to save you time and money."

    prompt = f"""
    You are a Top 1% Freelancer named Jules. Write a short, punchy bid (in English) for this project:
    Project: {titulo}
    Context: {desc}

    Structure:
    1. Professional greeting.
    2. {niche_sentence}
    3. Call to Action (Let's discuss).

    IMPORTANT: Do NOT include placeholders like [Your Name]. Sign as 'Jules'.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        base_proposal = chat_completion.choices[0].message.content

        # Injeção de Portfólio no final
        final_proposal = f"{base_proposal}\n\nCheck my portfolio here: {portfolio_link}"
        return final_proposal

    except Exception as e:
        return f"Erro no Groq: {e}"

def criar_botoes(project_id, link):
    markup = InlineKeyboardMarkup()
    btn_link = InlineKeyboardButton("🔗 Ver no Site", url=link)
    btn_send = InlineKeyboardButton("🚀 Enviar Proposta", callback_data=f"send_{project_id}")
    markup.add(btn_link, btn_send)
    return markup

def scan_fast_cash():
    if not bot or not FLN_TOKEN: return

    logger.info("📡 Varredura Groq iniciada...")
    # Seus nichos favoritos
    queries = ["python automation scraping", "market research", "video creation ai"]

    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")

        for q in queries:
            search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
            result = search_projects(session, query=q, search_filter=search_filter)

            if result and 'projects' in result:
                for p in result['projects'][:2]:
                    project_id = p.get('id')
                    min_b = p.get('budget', {}).get('minimum')
                    curr = p.get('currency', {}).get('code', 'UNK')

                    # --- FILTROS DE ELITE (ANTI-SCAM) ---
                    # 1. Budget Mínimo
                    if min_b is None or min_b < 15: continue

                    # 2. Moeda Forte
                    if curr not in ['USD', 'EUR', 'GBP', 'AUD', 'CAD']: continue

                    # 3. Localização do Cliente (Tier 1) - Simulado pois a API básica nem sempre retorna user country direto no search
                    # Para garantir, focamos na moeda que já filtra 90%

                    # 4. Palavras-chave proibidas (Blacklist simples)
                    title = p.get('title')
                    desc = p.get('preview_description', '')
                    if any(bad in title.lower() for bad in ["student", "homework", "urgent low budget", "simple task $5"]):
                        logger.info(f"🚫 Ignorado (Low Quality): {title}")
                        continue

                    link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"

                    logger.info(f"⚡ Groq gerando proposta para: {title}")
                    proposta = gerar_proposta_ia(title, desc)
                    
                    # Salva dados para o callback usar
                    PENDING_BIDS[str(project_id)] = {
                        "proposal": proposta,
                        "amount": min_b,
                        "currency": curr,
                        "title": title
                    }

                    msg = (
                        f"🚀 *ALVO ELITE DETECTADO*\n\n"
                        f"📝 *Projeto:* {title}\n"
                        f"💰 *Valor:* {min_b} {curr}\n\n"
                        f"⚡ *PROPOSTA GROQ (+Portfolio):*\n```\n{proposta}\n```"
                    )

                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=criar_botoes(project_id, link))
                    time.sleep(2)
            time.sleep(1)

    except Exception as e:
        logger.error(f"❌ Erro: {e}")

if bot:
    @bot.callback_query_handler(func=lambda call: call.data.startswith("send_"))
    def callback_send_bid(call):
        try:
            project_id = call.data.split("_")[1]
            bid_data = PENDING_BIDS.get(project_id)

            if not bid_data:
                bot.answer_callback_query(call.id, "⚠️ Dados da proposta expiraram.")
                return

            bot.answer_callback_query(call.id, "🚀 Enviando lance...")

            session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
            my_user_id = get_self_user_id(session)

            place_project_bid(
                session,
                project_id=int(project_id),
                bidder_id=my_user_id,
                amount=bid_data["amount"],
                period=7,
                milestone_percentage=100,
                description=bid_data["proposal"]
            )

            bot.edit_message_text(
                f"✅ *LANCE ENVIADO COM SUCESSO!*\n\n"
                f"🎯 *Projeto:* {bid_data['title']}\n"
                f"💰 *Valor:* {bid_data['amount']} {bid_data['currency']}\n",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            logger.info(f"✅ Lance enviado para projeto {project_id}")

        except Exception as e:
            logger.error(f"❌ Erro ao enviar lance: {e}")
            bot.answer_callback_query(call.id, f"Erro: {str(e)[:50]}")

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
