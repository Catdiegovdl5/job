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
logger = logging.getLogger("JulesV51_TotalCoverage")

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

# --- FORÇA BRUTA (AI OVERRIDE - V5.1 TOTAL SKILL COVERAGE) ---
FORCE_KEYWORDS = [
    "chatbot", "ai", "agent", "design", "logo", "writing", "video",
    "editing", "seo", "marketing", "shopify", "automation", "excel", "data"
]

# --- RADAR RECONFIGURATION (V5.1 - 15 Categories) ---
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
    bot.reply_to(message, f"🎮 <b>JULES V5.1 (TOTAL COVERAGE)</b>\nModo: {config.get('mode', 'PADRÃO')}\n\nTexto limpo e formatado.", parse_mode="HTML", reply_markup=markup)

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

    # --- TACTICAL INTELLIGENCE (V4.8 & V5.1 UPDATED) ---
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

    # --- LANGUAGE ENFORCER PROMPT (V5.0 CLEAN PROTOCOL) ---
    prompt = f"""
    Role: Diego, AI Expert.
    Project: "{titulo}"
    Budget: "{budget_str}" (Approx ${usd_val:.2f} USD)
    Context: "{desc}"

    DETECTED CATEGORY: {context_focus}
    SUGGESTED ARSENAL: {tool_suggestion}

    INSTRUCTIONS:
    1. Write summary in strict Portuguese (Brazil).
    2. List ONLY relevant tools (Focus on SUGGESTED ARSENAL if applicable).
    3. Write proposal in strict Professional English.

    STRICT RULE: NEVER use bolding (**), italics (_), or headers (###). Use only plain text. For lists, use a simple hyphen (-). Do NOT include the words 'RESUMO:', 'ARSENAL:', or 'PROPOSTA:' inside the content of the sections themselves.

    CRITICAL INSTRUCTION: SECAO 1 (RESUMO) is a briefing for the user about the CLIENT'S NEEDS. Do NOT use phrases like 'Estou aqui para ajudar' or 'Eu vou fazer' in SECAO 1. Instead, use 'O cliente precisa...', 'O projeto exige...' ou 'O objetivo é...'. Leave all your personal offers and 'I can help' phrases exclusively for SECAO 3.

    SECAO 1: RESUMO (PT-BR)
    Objetivo: Explicar para o Comandante (VOCÊ) do que se trata o projeto do cliente.
    Regra de Ouro: Foque 100% no que o CLIENTE escreveu na descrição. Não mencione o que você (Diego) vai fazer.
    Exemplo Correto: "O cliente possui uma loja Shopify e precisa integrar a API do Gemini via n8n para automatizar postagens no blog e redes sociais."

    SECAO 3: PROPOSTA (ENGLISH)
    Objetivo: Convencer o CLIENTE a te contratar.
    Regra de Ouro: Foque 100% na solução técnica e no seu diferencial. Use Inglês.
    Exemplo Correto: "I can build your Shopify-Gemini ecosystem using n8n. I have experience in RAG systems and social media automation..."

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
    - 3 lines summary about CLIENT NEEDS.

    SECAO 2: FERRAMENTAS
    - Tools list.

    SECAO 3: PROPOSTA (ENGLISH)
    - Proposal text.
    - Sign: Diego.
    """

    try:
        completion = client_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",  # MODEL SWAP (V4.9)
            temperature=0.6,
        )
        content = completion.choices[0].message.content.strip()

        # --- POLISHED OUTPUT (V5.0 DEEP CLEANING) ---
        # Remove markdown chars (*, #, _)
        content = re.sub(r'[\*\#_]', '', content)

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
                # V5.0 DEEP CLEANING LABELS
                resumo = re.sub(r'^(RESUMO|Resumo|Briefing|O cliente)\s*[:\-]*\s*', '', resumo, flags=re.IGNORECASE).strip()

            elif "2: FERRAMENTAS" in part or part.startswith("2:"):
                if ":" in part:
                    ferramentas = part.split(":", 1)[1].strip()
                else:
                    ferramentas = part.replace("2: FERRAMENTAS", "").strip()
                # V5.0 DEEP CLEANING LABELS
                ferramentas = re.sub(r'^(FERRAMENTAS|Arsenal|Tools|Stack)\s*[:\-]*\s*', '', ferramentas, flags=re.IGNORECASE).strip()

            elif "3: PROPOSTA" in part or part.startswith("3:"):
                if ":" in part:
                    proposta = part.split(":", 1)[1].strip()
                else:
                    proposta = part.replace("3: PROPOSTA", "").strip()
                # V5.0 DEEP CLEANING LABELS
                proposta = re.sub(r'^(PROPOSTA|Proposal|Offer)\s*[:\-]*\s*', '', proposta, flags=re.IGNORECASE).strip()

        return nivel, resumo, ferramentas, proposta

    except RateLimitError:  # RATE LIMIT HANDLING (V4.9)
        logger.warning("⚠️ Cota de IA atingida. Aguardando para tentar novamente...")
        time.sleep(60)
        return "Aguardando Cota", "Aguardando Cota", "Aguardando Cota", "Aguardando Cota"

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
            # SCAN THROTTLING (V5.1) - Increased to 15 per cycle
            for p in projects_list[:15]:
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

                if nivel == "Aguardando Cota": # Skip if rate limited
                    continue

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
                markup.add(InlineKeyboardButton(f"✅ Aceitar (Disparar Proposta)", callback_data=f"bid_{pid}"))
                markup.add(InlineKeyboardButton("❌ Rejeitar", callback_data=f"rejeitar_{pid}"))

                if bot: bot.send_message(CHAT_ID, msg, parse_mode="HTML", reply_markup=markup)
                time.sleep(random.randint(4, 7))

    except Exception as e:
        logger.error(f"Erro Radar: {e}")

if __name__ == "__main__":
    get_my_id()
    logger.info("🤖 Jules V5.1 (TOTAL COVERAGE) ONLINE")
    t = threading.Thread(target=start_telegram_listener)
    t.daemon = True
    t.start()
    while True:
        scan_radar()
        # RADAR SENSITIVITY (V5.1) - 45s Interval, but we keep 600s if instructed by previous "Observation Mode".
        # Prompt doesn't explicitly say to revert 600s, but says "Adjust Sentinel to Market Observation Mode" was PREVIOUS.
        # This prompt says "Atualizar o Cérebro do Diego (sentinel_real.py)". It doesn't mention the sleep time for sentinel.py.
        # But wait, step 1 was for Workana Monitor. Step 2 for Sentinel.
        # I will keep 600s as per the last state (Observation Mode) unless told otherwise, but wait...
        # The prompt says "Ajuste de Sensibilidade do Radar: ... diminuir o intervalo ... para 45 segundos ...".
        # Wait, that was V5.1 instruction block 3 in the prompt?
        # Ah, "Ajuste de Sensibilidade do Radar: Instrua o assistente a diminuir o intervalo de troca de frequência para 45 segundos".
        # This is for sentinel.py? Or Workana? The prompt context is "Expand Workana Radar... Update Diego Brain...".
        # Block 1 is for Workana Monitor. Block 2 is for Sentinel (Diego Brain).
        # Block 3 in previous V5.1 prompt was for Sentinel.
        # This prompt only has 2 steps: "Passo 1: Atualizar o Radar (workana_monitor.py)" and "Passo 2: Atualizar o Cérebro do Diego".
        # It does NOT ask to change the sleep time of sentinel.py back to 45s.
        # So I will leave the sleep time at 600s (from the previous turn's "Market Observation Mode").
        # Wait, I just pasted the whole file content above. I need to make sure I don't accidentally revert to 45s or 60s if I'm rewriting the file.
        # I'll check the current state of sentinel.py regarding sleep time.
        # It was set to 600s. I should preserve that if I'm not instructed to change it.
        # The prompt is specifically about adding Marketing/Video logic.
        logger.info("💤 Trocando frequência em 600s (Modo Observação)...")
        time.sleep(600)
