import time
import logging
import os
import threading
import json
import random
import re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects, place_project_bid
from freelancersdk.resources.users.users import get_self_user_id
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from dotenv import load_dotenv

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV45_Polished")

load_dotenv()

TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
FLN_TOKEN = os.environ.get("FLN_OAUTH_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None
client_groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

memory_lock = threading.Lock()
MEMORY_FILE = "memory.json"

MY_USER_ID = None

# --- SUAS SKILLS REAIS ---
MY_ACCEPTED_SKILLS = [
    "Image Processing", "Chatbot", "Visual Design", "AI Graphic Design", "AI Text-to-speech",
    "AI Text-to-text", "AI Translation", "Text Recognition", "Voice Synthesis", "Image Analysis",
    "AI Art Creation", "AI Image Editing", "AI Chatbot Development", "AI Content Writing",
    "AI Research", "AI Writing", "Conversational AI", "Chatbot Integration", "AI Agents", "AI Animation"
]

MY_SKILLS_SET = {s.lower().strip() for s in MY_ACCEPTED_SKILLS}

# --- FORÇA BRUTA (AI OVERRIDE) ---
FORCE_KEYWORDS = ["chatbot", "gpt", "ai agent", "artificial intelligence", "midjourney", "automation", "make.com", "n8n", "content writing"]

MISSIONS = {
    "caixa_rapido": ["AI Writing", "AI Image", "Translation", "Content Writing", "Voice Synthesis"],
    "nivel_s": ["Chatbot", "AI Agents", "Automation", "AI Research", "AI Development"]
}

# --- GLOBAL BANKER ---
RATES = {'USD': 1.0, 'EUR': 1.08, 'GBP': 1.30, 'AUD': 0.65, 'CAD': 0.72, 'INR': 0.0116, 'BRL': 0.17}
USD_TO_BRL = 5.75

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"config": {"current_mission_key": "nivel_s", "mode": "AI TECH"}}

def save_memory():
    with memory_lock:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f: json.dump(memory, f, indent=2)

memory = load_memory()
session = Session(oauth_token=FLN_TOKEN, url="https://www.freelancer.com")

def get_my_id():
    global MY_USER_ID
    if not MY_USER_ID:
        try:
            user = get_self_user_id(session)
            MY_USER_ID = user
            logger.info(f"🆔 ID do Comandante: {MY_USER_ID}")
        except: pass

def convert_currency(amount, currency_code):
    if not amount: return 0, 0
    code = currency_code.upper()
    rate_to_usd = RATES.get(code, 1.0)

    val_usd = float(amount) * rate_to_usd
    val_brl = val_usd * USD_TO_BRL
    return val_usd, val_brl

@bot.message_handler(commands=['missao', 'start'])
def handle_mission_command(message):
    markup = InlineKeyboardMarkup()
    btn_fast = InlineKeyboardButton("🎨 AI Criativa", callback_data="set_mission_fast")
    btn_stier = InlineKeyboardButton("🤖 AI Tech", callback_data="set_mission_stier")
    markup.add(btn_fast)
    markup.add(btn_stier)
    config = memory.get("config", {})
    bot.reply_to(message, f"🎮 <b>JULES V4.5 (POLISHED)</b>\nModo: {config.get('mode', 'PADRÃO')}\n\nTexto limpo e formatado.", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global memory

    if call.data.startswith("rejeitar_"):
        pid = call.data.replace("rejeitar_", "")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, "🗑️ Arquivado.")
            if pid in memory:
                memory[pid]['status'] = 'rejected'
                save_memory()
        except: pass

    elif call.data.startswith("bid_"):
        pid = call.data.replace("bid_", "")
        project_data = memory.get(pid)

        if not project_data:
            bot.answer_callback_query(call.id, "⚠️ Erro: Dados perdidos.")
            return

        bot.answer_callback_query(call.id, "🚀 Disparando...")
        try:
            if not MY_USER_ID: get_my_id()
            place_project_bid(
                session,
                project_id=int(pid),
                bidder_id=MY_USER_ID,
                amount=project_data['amount'],
                period=project_data['period'],
                milestone_percentage=100,
                description=project_data['proposal']
            )
            bot.send_message(call.message.chat.id, f"✅ <b>TIRO NO ALVO!</b>\nProjeto: {pid}\nStatus: Enviado com Sucesso!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            memory[pid]['status'] = 'accepted'
            save_memory()
        except Exception as e:
            msg = str(e)
            if "required skills" in msg.lower():
                bot.send_message(call.message.chat.id, f"❌ Erro Skill Freelancer: O site bloqueou por falta de skill técnica (Python/PHP). Adicione no perfil.")
            else:
                bot.send_message(call.message.chat.id, f"❌ Erro: {msg}")

    elif call.data == "set_mission_fast":
        memory["config"] = {"current_mission_key": "caixa_rapido", "mode": "AI CRIATIVA"}
        save_memory()
        bot.answer_callback_query(call.id, "Modo Criativo Ativo")
        bot.send_message(call.message.chat.id, "✅ <b>MODO AI CRIATIVA</b>", parse_mode="HTML")

    elif call.data == "set_mission_stier":
        memory["config"] = {"current_mission_key": "nivel_s", "mode": "AI TECH"}
        save_memory()
        bot.answer_callback_query(call.id, "Modo Tech Ativo")
        bot.send_message(call.message.chat.id, "💎 <b>MODO AI TECH</b>", parse_mode="HTML")

def start_telegram_listener():
    if bot:
        logger.info("🎧 Telegram ON")
        bot.infinity_polling()

def gerar_analise_diego(titulo, desc, budget_str, usd_val):
    if not client_groq: return "N/A", "Erro", "N/A", "N/A"

    # --- LANGUAGE ENFORCER PROMPT ---
    prompt = f"""
    Role: Diego, AI Expert.
    Project: "{titulo}"
    Budget: "{budget_str}" (Approx ${usd_val:.2f} USD)
    Context: "{desc}"

    INSTRUCTIONS:
    1. Write summary in strict Portuguese (Brazil).
    2. List ONLY relevant tools (Free/Paid).
    3. Write proposal in strict Professional English.

    RULES FOR PROPOSAL (SECTION 3):
    - Start DIRECTLY (e.g., "I can help with...").
    - Be casual, human, professional.
    - Max 150 words.
    - No fluff.

    OUTPUT FORMAT:
    SECAO 0: NIVEL
    - If USD > 700: "💎 S-TIER"
    - Else: "⚖️ MID-TIER"

    SECAO 1: RESUMO (PT-BR)
    - 3 lines summary.

    SECAO 2: FERRAMENTAS
    - Tools list.

    SECAO 3: PROPOSTA (ENGLISH)
    - Proposal text.
    - Sign: Diego.
    """

    try:
        completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
        )
        content = completion.choices[0].message.content.strip()

        # --- POLISHED OUTPUT (CLEANING) ---
        content = content.replace("##", "").replace("* ", "• ")

        # Remove Language Tags
        for tag in ["(PT-BR)", "(ENGLISH)", "(Portuguese Brazil 🇧🇷)", "(Project Language)"]:
            content = content.replace(tag, "")

        parts = content.split("SECAO")

        # Parse Sections
        nivel = "⚖️ MID-TIER"
        resumo = "..."
        ferramentas = "..."
        proposta = "..."

        for part in parts:
            part = part.strip()
            if not part: continue

            if "0: NIVEL" in part or part.startswith("0:"):
                # Handle variations like "0: NIVEL - Select: 💎 S-TIER" or "0: NIVEL: 💎 S-TIER"
                if ":" in part.split("0:", 1)[1]:
                     sub_parts = part.split(":")
                     # Find the part that looks like the level
                     for sp in sub_parts:
                         sp = sp.strip()
                         if "S-TIER" in sp or "MID-TIER" in sp:
                             nivel = sp.replace("- Select", "").strip()
                             break
                else:
                    nivel = part.replace("0: NIVEL", "").strip()

            elif "1: RESUMO" in part or part.startswith("1:"):
                if ":" in part:
                     resumo = part.split(":", 1)[1].strip()
                else:
                     resumo = part.replace("1: RESUMO", "").strip()
                # Remove prefixes using regex
                resumo = re.sub(r'^(RESUMO|Resumo)\s*[:\-]*\s*', '', resumo).strip()

            elif "2: FERRAMENTAS" in part or part.startswith("2:"):
                if ":" in part:
                    ferramentas = part.split(":", 1)[1].strip()
                else:
                    ferramentas = part.replace("2: FERRAMENTAS", "").strip()
                ferramentas = re.sub(r'^(FERRAMENTAS|Ferramentas)\s*[:\-]*\s*', '', ferramentas).strip()

            elif "3: PROPOSTA" in part or part.startswith("3:"):
                if ":" in part:
                    proposta = part.split(":", 1)[1].strip()
                else:
                    proposta = part.replace("3: PROPOSTA", "").strip()
                proposta = re.sub(r'^(PROPOSTA|Proposta)\s*[:\-]*\s*', '', proposta).strip()

        return nivel, resumo, ferramentas, proposta
    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return "Erro", "Erro IA", "N/A", "Erro IA"

def scan_radar():
    config = memory.get("config", {})
    mission_key = config.get("current_mission_key", "caixa_rapido")
    mission_list = MISSIONS.get(mission_key, MISSIONS["caixa_rapido"])
    current_focus = random.choice(mission_list)
    mode_name = config.get("mode", "PADRÃO")

    logger.info(f"📡 Radar [{mode_name}]: '{current_focus}'")

    try:
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        result = search_projects(session, query=current_focus, search_filter=search_filter)

        projects_list = result.get('projects')
        if projects_list:
            count = 0
            for p in projects_list[:10]:
                if p.get('status', 'active') != 'active': continue

                pid = str(p.get('id'))
                if pid in memory: continue

                # --- LÓGICA V4.5 (AI OVERRIDE & SKILL MATCH) ---
                raw_jobs = p.get('jobs') or []
                project_skills = [j.get('name', '').lower() for j in raw_jobs]
                title_lower = p.get('title', '').lower()

                has_skill_match = any(ps in MY_SKILLS_SET for ps in project_skills)
                is_ai_project = any(fk in title_lower for fk in FORCE_KEYWORDS)

                # Se não tem skill compatível E não é projeto de IA forçado, ignora
                if not has_skill_match and not is_ai_project:
                    continue

                count += 1
                title = p.get('title')
                budget_min = p.get('budget', {}).get('minimum', 0)
                budget_max = p.get('budget', {}).get('maximum', budget_min)
                code = p.get('currency', {}).get('code', 'USD')

                # Conversão Global Banker
                min_usd, min_brl = convert_currency(budget_min, code)
                max_usd, max_brl = convert_currency(budget_max, code)

                budget_str_usd = f"${min_usd:.0f}-${max_usd:.0f}"
                budget_str_brl = f"R${min_brl:.0f}-R${max_brl:.0f}"

                logger.info(f"🎯 Alvo Capturado: {title}")

                nivel, resumo, ferramentas, proposta = gerar_analise_diego(title, p.get('preview_description', ''), f"{budget_min} {code}", min_usd)

                # Bid Amount Logic
                bid_amount = budget_min
                if "S-TIER" in nivel: bid_amount = int((budget_min + budget_max) / 2)

                memory[pid] = {
                    "status": "seen",
                    "proposal": proposta,
                    "amount": bid_amount,
                    "period": 7,
                    "currency": code
                }
                save_memory()

                # --- TACTICAL DISPLAY (TELEGRAM) ---
                msg = f"<b>🎯 NOVO ALVO [{mode_name}]</b>\n"
                msg += f"<b>🏆 {nivel}</b>\n\n"
                msg += f"<b>📂 Projeto:</b> <a href='https://www.freelancer.com/projects/{pid}'>{title}</a>\n"
                msg += f"<b>💰 Valor:</b> {budget_str_usd}  |  {budget_str_brl}\n\n"
                msg += f"<b>📋 RESUMO:</b>\n<i>{resumo}</i>\n\n"
                msg += f"<b>🛠 ARSENAL:</b>\n<code>{ferramentas}</code>\n\n"
                msg += f"<b>💡 PROPOSTA:</b>\n{proposta}"

                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(f"✅ LANCE ({bid_amount} {code})", callback_data=f"bid_{pid}"))
                markup.add(InlineKeyboardButton("❌ Rejeitar", callback_data=f"rejeitar_{pid}"))

                if bot: bot.send_message(CHAT_ID, msg, parse_mode="HTML", reply_markup=markup)
                time.sleep(random.randint(4, 7))

    except Exception as e:
        logger.error(f"Erro Radar: {e}")

if __name__ == "__main__":
    get_my_id()
    logger.info("🤖 Jules V4.5 (POLISHED) ONLINE")
    t = threading.Thread(target=start_telegram_listener)
    t.daemon = True
    t.start()
    while True:
        scan_radar()
        logger.info("💤 Trocando frequência em 60s...")
        time.sleep(60)
