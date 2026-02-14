import time
import logging
import os
import threading
import http.server
import socketserver
import json
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from dotenv import load_dotenv

# Carrega chaves do arquivo .env (apenas para rodar local)
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV17")

TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
API_SECRET = os.environ.get("API_SECRET", "1234")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
memory_lock = threading.Lock()
MEMORY_FILE = "memory.json"

def load_memory():
    with memory_lock:
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    data = json.load(f)
                    if "current_mission" not in data:
                        data["current_mission"] = "python automation scraping"
                    return data
            except: pass
        return {"current_mission": "python automation scraping"}

memory = load_memory()

def gerar_proposta_diego(titulo, desc):
    if not GEMINI_API_KEY: return "⚠️ Configure GEMINI_API_KEY."
    prompt = f"Role: Diego, Solutions Architect. Task: Technical bid for '{titulo}'. Content: {desc}. Rules: No markdown, plain text only, start with technical solution, sign 'Diego'."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        texto = data['candidates'][0]['content']['parts'][0]['text']
        return texto.replace("**", "").replace("Jules", "Diego").strip()
    except Exception as e:
        return f"Erro Gemini: {str(e)}"

def scan_radar():
    with memory_lock:
        if not bot or not FLN_TOKEN: return
        query = memory.get("current_mission")

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
                texto = gerar_proposta_diego(title, p.get('preview_description', ''))
                msg = bot.send_message(CHAT_ID, f"🎯 *ALVO*\n📝 {title}\n\n{texto}", parse_mode="Markdown")

                with memory_lock:
                    memory[pid] = {'alert_id': msg.message_id}
                    with open(MEMORY_FILE, "w") as f: json.dump(memory, f)
    except Exception as e: logger.error(f"Erro Radar: {e}")

class APIHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.headers.get('X-Api-Key') != API_SECRET:
            self.send_response(403); self.end_headers(); return
        if self.path == "/api/set_mode":
            content_len = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_len))
            new_mode = data.get("mode")
            with memory_lock:
                memory["current_mission"] = new_mode
            bot.send_message(CHAT_ID, f"📡 [OPAL] Modo: {new_mode.upper()}")
            self.send_response(200); self.end_headers()

if __name__ == "__main__":
    threading.Thread(target=lambda: socketserver.TCPServer(("", int(os.environ.get("PORT", 10000))), APIHandler).serve_forever(), daemon=True).start()
    while True:
        scan_radar()
        time.sleep(180)
