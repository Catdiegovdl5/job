import time
import logging
import os
import threading
import json
import random
import re
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from groq import Groq, RateLimitError
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects, place_project_bid
from freelancersdk.resources.users.users import get_self_user_id
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from dotenv import load_dotenv

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("JulesV653_DualOption")

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

# --- FORÇA BRUTA ---
FORCE_KEYWORDS = [
    "chatbot", "ai", "agent", "design", "logo", "writing", "video",
    "editing", "seo", "marketing", "shopify", "automation", "excel", "data"
]

# --- RADAR RECONFIGURATION ---
MISSIONS = {
    "caixa_rapido": [
        "Data Entry", "Excel", "Graphic Design", "Logo Design", "Photoshop",
        "SEO", "Article Writing", "Virtual Assistant", "Photo Editing",
        "Content Writing", "Social Media Marketing", "Copywriting",
        "Research", "Translation", "Product Descriptions"
    ],
    "nivel_s": [
        "Artificial Intelligence", "Chatbot", "Video Editing", "Shopify",
        "Automation", "AI Agents", "n8n", "Make.com", "Digital Marketing",
        "Facebook Ads", "Animation", "Data Analysis", "Prompt Engineering",
        "Conversational AI", "E-commerce"
    ]
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
    bot.reply_to(message, f"🎮 <b>JULES V6.5.3 (DUAL OPTION)</b>\nModo: {config.get('mode', 'PADRÃO')}\n\nTexto limpo e formatado.", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # This handler is specific to Sentinel (Freelancer.com).
    # Workana Sentinel has its own handler logic in workana_sentinel.py,
    # BUT since they share this 'bot' instance if running separately, it's fine.
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
        # This block is for Freelancer.com API bidding
        pid = call.data.replace("bid_", "")
        project_data = memory.get(pid)

        if not project_data:
            bot.answer_callback_query(call.id, "⚠️ Erro: Dados perdidos.")
            return

        bot.answer_callback_query(call.id, "🚀 Disparando...")
        try:
            if not MY_USER_ID: get_my_id()
            # For Freelancer.com, we use 'opc_a' as default or 'proposal' if old format
            prop_text = project_data.get('opc_a', project_data.get('proposal', 'Hi, I can help.'))

            place_project_bid(
                session,
                project_id=int(pid),
                bidder_id=MY_USER_ID,
                amount=project_data['amount'],
                period=project_data['period'],
                milestone_percentage=100,
                description=prop_text
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
    if not client_groq: return "N/A", "Erro", "N/A", "N/A", "N/A"

    # --- TACTICAL INTELLIGENCE ---
    titulo_lower = titulo.lower()
    desc_lower = desc.lower()

    context_focus = "General"
    tool_suggestion = "Best available tools"

    is_chatbot_auto = any(k in titulo_lower or k in desc_lower for k in ["chatbot", "automation", "agent", "python", "script", "scraping", "n8n", "make", "development"])
    is_content = any(k in titulo_lower or k in desc_lower for k in ["writing", "translation", "content", "copy", "text", "seo", "article", "blog"])
    is_visual = any(k in titulo_lower or k in desc_lower for k in ["design", "image", "logo", "art ", "visual", "photo", "graphic"])
    is_marketing = any(k in titulo_lower or k in desc_lower for k in ["marketing", "ads", "traffic", "tráfego", "seo", "google ads", "meta ads", "facebook ads"])
    is_video = any(k in titulo_lower or k in desc_lower for k in ["video", "edição", "editing", "youtube", "reels", "tiktok", "premiere", "after effects"])

    if is_marketing:
        context_focus = "Digital Marketing & Online Traffic"
        tool_suggestion = "Google Ads, Meta Ads Manager, Google Analytics 4, SEMrush, Search Console"
    elif is_video:
        context_focus = "Video Editing & Motion Graphics"
        tool_suggestion = "Adobe Premiere Pro, After Effects, CapCut (AI features), DaVinci Resolve"
    elif is_chatbot_auto:
         context_focus = "Chatbot & Automation"
         tool_suggestion = "OpenAI API, n8n, Make.com, Python, LangChain"
    elif is_content:
         context_focus = "Content Writing & Translation"
         tool_suggestion = "GPT-4o, Claude 3.5 Sonnet, SEO Surfer, Jasper"
    elif is_visual:
         context_focus = "Visual Design & Image Generation"
         tool_suggestion = "Midjourney, Photoshop (Firefly), Canva, Stable Diffusion"

    # --- LANGUAGE ENFORCER PROMPT (V6.5.3 DUAL OPTION) ---
    prompt = f"""
    Role: Diego, AI Expert.
    Project: "{titulo}"
    Budget: "{budget_str}" (Approx ${usd_val:.2f} USD)
    Context: "{desc}"

    DETECTED CATEGORY: {context_focus}
    SUGGESTED ARSENAL: {tool_suggestion}

    INSTRUCTIONS:
    1. Write SECAO 1 (Summary) in strict Portuguese (Brazil).
    2. Write SECAO 3 (Option A - Direct Proposal) in the SAME LANGUAGE as the Project Description. Short, punchy, "I can do this" style.
    3. Write SECAO 4 (Option B - Persuasive Proposal) in the SAME LANGUAGE as the Project Description. Detailed, "Here is my approach" style.

    CRITICAL: Never mention you are an AI. Be human, direct, and professional. Do NOT include markdown headers inside content.

    OUTPUT FORMAT:
    SECAO 0: NIVEL
    - If USD > 700: "💎 S-TIER"
    - Else: "⚖️ MID-TIER"

    SECAO 1: RESUMO (PT-BR)
    - 3 lines summary about CLIENT NEEDS.

    SECAO 2: FERRAMENTAS
    - Tools list.

    SECAO 3: OPC_A
    - Option A text (Direct).

    SECAO 4: OPC_B
    - Option B text (Persuasive).
    """

    try:
        completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.6,
        )
        content = completion.choices[0].message.content.strip()

        # --- POLISHED OUTPUT (V5.0 DEEP CLEANING) ---
        content = re.sub(r'[\*\#_]', '', content)
        for tag in ["(PT-BR)", "(ENGLISH)", "(Portuguese Brazil 🇧🇷)", "(Project Language)"]:
            content = content.replace(tag, "")

        parts = content.split("SECAO")

        # Parse Sections
        nivel = "⚖️ MID-TIER"
        resumo = "..."
        ferramentas = "..."
        opc_a = "..."
        opc_b = "..."

        for part in parts:
            part = part.strip()
            if not part: continue

            if "0: NIVEL" in part or part.startswith("0:"):
                if ":" in part.split("0:", 1)[1]:
                     sub_parts = part.split(":")
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
                resumo = re.sub(r'^(RESUMO|Resumo|Briefing|O cliente)\s*[:\-]*\s*', '', resumo, flags=re.IGNORECASE).strip()

            elif "2: FERRAMENTAS" in part or part.startswith("2:"):
                if ":" in part:
                    ferramentas = part.split(":", 1)[1].strip()
                else:
                    ferramentas = part.replace("2: FERRAMENTAS", "").strip()
                ferramentas = re.sub(r'^(FERRAMENTAS|Arsenal|Tools|Stack)\s*[:\-]*\s*', '', ferramentas, flags=re.IGNORECASE).strip()

            elif "3: OPC_A" in part or part.startswith("3:"):
                if ":" in part:
                    opc_a = part.split(":", 1)[1].strip()
                else:
                    opc_a = part.replace("3: OPC_A", "").strip()
                opc_a = re.sub(r'^(OPC_A|Option A|Direct)\s*[:\-]*\s*', '', opc_a, flags=re.IGNORECASE).strip()

            elif "4: OPC_B" in part or part.startswith("4:"):
                if ":" in part:
                    opc_b = part.split(":", 1)[1].strip()
                else:
                    opc_b = part.replace("4: OPC_B", "").strip()
                opc_b = re.sub(r'^(OPC_B|Option B|Persuasive)\s*[:\-]*\s*', '', opc_b, flags=re.IGNORECASE).strip()

        return nivel, resumo, ferramentas, opc_a, opc_b

    except RateLimitError:
        logger.warning("⚠️ Cota de IA atingida. Aguardando para tentar novamente...")
        time.sleep(60)
        return "Aguardando Cota", "Aguardando Cota", "Aguardando Cota", "Aguardando Cota", "Aguardando Cota"

    except Exception as e:
        logger.error(f"Erro na IA: {e}")
        return "Erro", "Erro IA", "N/A", "Erro IA", "Erro IA"

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
            for p in projects_list[:15]:
                if p.get('status', 'active') != 'active': continue

                pid = str(p.get('id'))
                if pid in memory: continue

                raw_jobs = p.get('jobs') or []
                project_skills = [j.get('name', '').lower() for j in raw_jobs]
                title_lower = p.get('title', '').lower()

                has_skill_match = any(ps in MY_SKILLS_SET for ps in project_skills)
                is_ai_project = any(fk in title_lower for fk in FORCE_KEYWORDS)

                if not has_skill_match and not is_ai_project:
                    continue

                count += 1
                title = p.get('title')
                budget_min = p.get('budget', {}).get('minimum', 0)
                budget_max = p.get('budget', {}).get('maximum', budget_min)
                code = p.get('currency', {}).get('code', 'USD')

                min_usd, min_brl = convert_currency(budget_min, code)
                max_usd, max_brl = convert_currency(budget_max, code)

                budget_str_usd = f"${min_usd:.0f}-${max_usd:.0f}"
                budget_str_brl = f"R${min_brl:.0f}-R${max_brl:.0f}"

                logger.info(f"🎯 Alvo Capturado: {title}")

                nivel, resumo, ferramentas, opc_a, opc_b = gerar_analise_diego(title, p.get('preview_description', ''), f"{budget_min} {code}", min_usd)

                if nivel == "Aguardando Cota":
                    continue

                bid_amount = budget_min
                if "S-TIER" in nivel: bid_amount = int((budget_min + budget_max) / 2)

                memory[pid] = {
                    "status": "seen",
                    "opc_a": opc_a,
                    "opc_b": opc_b,
                    "proposal": opc_a, # Fallback for old bid logic
                    "amount": bid_amount,
                    "period": 7,
                    "currency": code
                }
                save_memory()

                msg = f"<b>🎯 NOVO ALVO [{mode_name}]</b>\n"
                msg += f"<b>🏆 {nivel}</b>\n\n"
                msg += f"<b>📂 Projeto:</b> <a href='https://www.freelancer.com/projects/{pid}'>{title}</a>\n"
                msg += f"<b>💰 Valor:</b> {budget_str_usd}  |  {budget_str_brl}\n\n"
                msg += f"<b>📋 RESUMO:</b>\n<i>{resumo}</i>\n\n"
                msg += f"<b>🛠 ARSENAL:</b>\n<code>{ferramentas}</code>\n\n"
                msg += f"<b>💡 OPÇÃO A (DIRETA):</b>\n{opc_a[:100]}...\n\n"

                markup = InlineKeyboardMarkup()
                # Adapting button to support Dual Option for Freelancer.com too, using opc_a by default for now via 'bid_'
                # Or we could implement wk_A_ logic here too if we want dual option on Freelancer.com.
                # For now, keeping the "Aceitar" (which uses opc_a/proposal) to not break existing flow unless requested.
                # The user request specifically mentioned updating `workana_monitor.py` for buttons.
                # But `sentinel.py` is the main brain, so it needs to return 5 values.
                markup.add(InlineKeyboardButton(f"✅ Aceitar (Opção A)", callback_data=f"bid_{pid}"))
                markup.add(InlineKeyboardButton("❌ Rejeitar", callback_data=f"rejeitar_{pid}"))

                if bot: bot.send_message(CHAT_ID, msg, parse_mode="HTML", reply_markup=markup)
                time.sleep(random.randint(4, 7))

    except Exception as e:
        logger.error(f"Erro Radar: {e}")

if __name__ == "__main__":
    get_my_id()
    logger.info("🤖 Jules V6.5.3 (DUAL OPTION) ONLINE")
    t = threading.Thread(target=start_telegram_listener)
    t.daemon = True
    t.start()
    while True:
        scan_radar()
        logger.info("💤 Trocando frequência em 600s (Modo Observação)...")
        time.sleep(600)
