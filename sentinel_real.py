import time
import logging
import os
import threading
import json
import telebot
import re
from groq import Groq
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV17_Groq")

# DIAGNOSTIC PROTOCOL: Log Absolute Path of .env
env_path = os.path.abspath(".env")
logger.info(f"🔎 DEBUG: Tentando carregar .env de: {env_path}")

# Carrega chaves do arquivo .env IMEDIATAMENTE (apenas para rodar local)
load_dotenv()

# DIAGNOSTIC PROTOCOL: Verificar Variaveis
def check_env_var(name):
    val = os.environ.get(name)
    if not val:
        logger.error(f"❌ ERRO CRITICO: Variável {name} não encontrada no .env ou sistema")
        return None
    return val

TG_TOKEN = check_env_var("TG_TOKEN")
CHAT_ID = check_env_var("TG_CHAT_ID")
FLN_TOKEN = check_env_var("FLN_OAUTH_TOKEN")
GROQ_API_KEY = check_env_var("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
try:
    client_groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
except Exception as e:
    logger.error(f"Erro ao inicializar Groq: {e}")
    client_groq = None

memory_lock = threading.Lock()
MEMORY_FILE = "memory.json"

def escape_markdown(text):
    if not text: return ""
    # Remove caracteres que costumam quebrar o Markdown do Telegram
    # Using proper escaping for backslashes in Python string within bash heredoc
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding='utf-8') as f:
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
            model="llama-3.3-70b-versatile",
            temperature=0.5,
        )
        content = chat_completion.choices[0].message.content
        # Reforço na regra de sanitização
        return content.replace("**", "").replace("###", "").strip()
    except Exception as e:
        return f"Erro Groq: {str(e)}"

def scan_radar():
    query = memory.get("current_mission", "python automation scraping")

    # Check token again just in case
    if not FLN_TOKEN:
         logger.error("❌ ERRO: FLN_OAUTH_TOKEN ausente. Radar abortado.")
         return

    try:
        # Robust Session Initialization
        try:
            session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")
        except Exception as session_error:
            logger.error(f"❌ ERRO AO INICIAR SESSÃO FREELANCER: {session_error}. Verifique se o token é válido.")
            return

        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=query, search_filter=search_filter)

        if result and 'projects' in result:
            for p in result['projects'][:2]:
                pid = str(p.get('id'))

                with memory_lock:
                    if pid in memory: continue

                title = p.get('title')
                logger.info(f"Processando alvo: {title}")
                raw_text = gerar_proposta_diego(title, p.get('preview_description', ''))

                # Sanitização de Saída
                safe_title = escape_markdown(title)
                safe_text = escape_markdown(raw_text)

                if bot:
                    bot.send_message(CHAT_ID, f"🎯 *NOVO ALVO ENCONTRADO*\n\n📝 *Projeto:* {safe_title}\n💰 {p.get('budget', {}).get('minimum', '?')} USD\n\n{safe_text}", parse_mode="Markdown")

                with memory_lock:
                    memory[pid] = True
                    with open(MEMORY_FILE, "w", encoding='utf-8') as f: json.dump(memory, f)

                time.sleep(2)
    except Exception as e:
        logger.error(f"Erro no Radar (Geral): {e}")

if __name__ == "__main__":
    logger.info("🤖 Jules V17 (Groq Edition) ONLINE no PC DIEGO")

    # Log de Inicio (Masked)
    def mask(val): return f"{val[:4]}..." if val and len(val) > 4 else "MISSING"

    logger.info(f"🔧 CONFIG LOADED: TG_TOKEN={mask(TG_TOKEN)}")
    logger.info(f"🔧 CONFIG LOADED: FLN_TOKEN={mask(FLN_TOKEN)}")
    logger.info(f"🔧 CONFIG LOADED: GROQ_KEY={mask(GROQ_API_KEY)}")

    while True:
        scan_radar()
        time.sleep(60)
