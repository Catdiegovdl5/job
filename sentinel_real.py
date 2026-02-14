import time
import logging
import os
import threading
import json
import telebot
from groq import Groq
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from dotenv import load_dotenv

# Carrega chaves do arquivo .env (apenas para rodar local)
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV17_Groq")

TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
try:
    client_groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except Exception as e:
    logger.error(f"Erro ao inicializar Groq: {e}")
    client_groq = None

memory_lock = threading.Lock()
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"current_mission": "python automation scraping"}

memory = load_memory()

def gerar_proposta_diego(titulo, desc):
    if not client_groq: return "⚠️ Erro: Groq não configurado."

    prompt = f"Role: Diego, Solutions Architect. Create a technical bid for: {titulo}. Description: {desc}. Rule: NO markdown, plain text only, be direct, sign 'Diego'."

    try:
        chat_completion = client_groq.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192",
            temperature=0.5,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro Groq: {str(e)}"

def scan_radar():
    query = memory.get("current_mission", "python automation scraping")

    try:
        session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=query, search_filter=search_filter)

        if result and 'projects' in result:
            for p in result['projects'][:2]:
                pid = str(p.get('id'))

                with memory_lock:
                    if pid in memory: continue

                title = p.get('title')
                logger.info(f"Processando alvo: {title}")
                texto = gerar_proposta_diego(title, p.get('preview_description', ''))

                if bot:
                    bot.send_message(CHAT_ID, f"🎯 *NOVO ALVO ENCONTRADO*\n\n📝 *Projeto:* {title}\n💰 {p.get('budget', {}).get('minimum', '?')} USD\n\n{texto}", parse_mode="Markdown")

                with memory_lock:
                    memory[pid] = True
                    with open(MEMORY_FILE, "w") as f: json.dump(memory, f)

                time.sleep(2)
    except Exception as e:
        logger.error(f"Erro no Radar: {e}")

if __name__ == "__main__":
    logger.info("🤖 Jules V17 (Groq Edition) ONLINE no PC DIEGO")
    while True:
        scan_radar()
        time.sleep(60)
