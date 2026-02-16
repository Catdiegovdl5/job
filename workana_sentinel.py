import asyncio
import json
import os
import time
import random
import re
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Importa a inteligência do Diego
try:
    from sentinel import gerar_analise_diego
except ImportError:
    try:
        from sentinel_real import gerar_analise_diego
    except ImportError:
        print("❌ Erro: Não foi possível importar 'gerar_analise_diego' de sentinel_real.py.")
        exit(1)

load_dotenv()
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
bot = telebot.TeleBot(TG_TOKEN)

# CONFIGURAÇÕES TÁTICAS
WORKANA_URL = "https://www.workana.com/jobs?language=en%2Cpt&skills=artificial-intelligence%2Cinternet-marketing%2Cvideo-editing"
AUTH_FILE = "workana_auth.json"
SEEN_PROJECTS_FILE = "workana_seen.json"
MEMORY_FILE_WK = "workana_memory.json"

# PERSISTÊNCIA DE MEMÓRIA (Para botões)
def load_memory_wk():
    if os.path.exists(MEMORY_FILE_WK):
        try:
            with open(MEMORY_FILE_WK, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_memory_wk():
    try:
        with open(MEMORY_FILE_WK, "w", encoding="utf-8") as f: json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"⚠️ Erro ao salvar memória Workana: {e}")

memory = load_memory_wk()

def load_seen():
    if os.path.exists(SEEN_PROJECTS_FILE):
        try:
            with open(SEEN_PROJECTS_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_seen(seen):
    with open(SEEN_PROJECTS_FILE, "w") as f: json.dump(seen, f)

async def disparar_proposta_workana(browser_context, project_link, proposal_text):
    """
    Módulo de Lance Automático para Workana.
    """
    page = await browser_context.new_page()
    try:
        print(f"🚀 Iniciando processo de lance automático para: {project_link}")
        await page.goto(project_link)

        try:
            btn_proposta = await page.wait_for_selector(".bid-button, .btn-primary, a[href*='/bid']", timeout=10000)
            if btn_proposta:
                await btn_proposta.click()
            else:
                print("⚠️ Botão de proposta não encontrado.")
                await page.close()
                return
        except Exception as e:
             print(f"⚠️ Erro ao buscar botão de proposta: {e}")
             await page.close()
             return

        wait_time = random.randint(30, 60)
        print(f"⏳ Simulando leitura humana ({wait_time}s)...")
        await asyncio.sleep(wait_time)

        try:
            textarea = await page.wait_for_selector("#BidDescription, [name='description'], textarea", timeout=10000)
            if textarea:
                await textarea.fill(proposal_text)
                print("✅ Texto da proposta preenchido.")
            else:
                print("⚠️ Campo de texto da proposta não encontrado.")
        except Exception as e:
             print(f"⚠️ Erro ao preencher proposta: {e}")

        print("✅ Processo de preenchimento concluído com sucesso!")
        await page.close()
    except Exception as e:
        print(f"❌ Falha no disparo automático: {e}")
        try:
            await page.close()
        except: pass

async def disparar_proposta_workana_with_context(link, text):
    """
    Wrapper to handle Playwright lifecycle for callback execution.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        try:
            context = await browser.new_context(storage_state=AUTH_FILE)
        except:
            context = await browser.new_context()

        await disparar_proposta_workana(context, link, text)
        await asyncio.sleep(5)
        await browser.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("wk_"))
def handle_workana_bid(call):
    # Formato: wk_OPCAO_ID (ex: wk_A_12345)
    try:
        parts = call.data.split("_")
        if len(parts) < 3: return
        opcao = parts[1]
        p_id = "_".join(parts[2:]) # Rejoin if ID had underscores

        project_data = memory.get(p_id)
        if not project_data:
            bot.answer_callback_query(call.id, "❌ Dados expirados.")
            return

        prop_text = project_data['opc_a'] if opcao == "A" else project_data['opc_b']
        bot.answer_callback_query(call.id, f"🚀 Disparando Opção {opcao}...")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(disparar_proposta_workana_with_context(project_data['link'], prop_text))
            loop.close()
        except Exception as e:
            print(f"Erro ao executar async no callback: {e}")

        bot.send_message(CHAT_ID, f"✅ <b>PROPOSTA {opcao} PREENCHIDA!</b>\nVerifique na Workana para o envio final.", parse_mode="HTML")
    except Exception as e:
        print(f"Erro no handler: {e}")

def start_telegram_listener():
    if bot:
        print("🎧 Telegram Listener (Workana) ON")
        bot.infinity_polling()

async def scan_workana():
    seen_ids = load_seen()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await browser.new_context(storage_state=AUTH_FILE)
        except Exception as e:
            print(f"⚠️ Erro ao carregar cookies: {e}")
            context = await browser.new_context()

        page = await context.new_page()
        print("\n📡 WORKANA: Varrendo a fortaleza...")

        try:
            await page.goto(WORKANA_URL, timeout=60000)
            await page.wait_for_selector(".project-item", timeout=15000)
        except Exception as e:
            print(f"⚠️ Erro ao acessar Workana: {e}")
            await browser.close()
            return

        projects = await page.query_selector_all(".project-item")
        print(f"🔎 Foram encontrados {len(projects)} projetos na página.")

        for p_item in projects[:20]:
            title_el = await p_item.query_selector(".project-title")
            title = (await title_el.inner_text()).strip() if title_el else "Sem Título"

            link_el = await p_item.query_selector(".project-title a")
            href = await link_el.get_attribute("href") if link_el else ""
            p_id = href.split('/')[-1] if href else None

            date_el = await p_item.query_selector(".date")
            date_text = (await date_el.inner_text()).lower() if date_el else "data n/a"

            print(f"--- Verificando: {title[:25]}... | ID: {p_id} | Data: {date_text}")

            if not p_id: continue

            # FILTRO DE 3 DIAS
            is_too_old = False
            if any(x in date_text for x in ["semana", "mês", "mes", "ano"]):
                is_too_old = True
            elif "dia" in date_text:
                days = re.findall(r'\d+', date_text)
                if days and int(days[0]) > 3:
                    is_too_old = True

            if is_too_old:
                print(f"   ⏭️ Ignorado: Antigo ({date_text})")
                continue

            if p_id in seen_ids:
                print(f"   ⏭️ Ignorado: Já enviado.")
                continue

            print(f"   🎯 ALVO APROVADO: {title}")

            desc_el = await p_item.query_selector(".project-details")
            desc = (await desc_el.inner_text()).strip() if desc_el else "Sem Descrição"

            budget_el = await p_item.query_selector(".budget")
            budget_str = (await budget_el.inner_text()).strip() if budget_el else "N/A"

            link = "https://www.workana.com" + href

            # Diego analisa o alvo (RETORNA 5 VALORES AGORA)
            nivel, resumo, arsenal, opc_a, opc_b = gerar_analise_diego(title, desc, budget_str, 50.0)

            # Guarda os dados na memória para o clique do botão no Telegram
            memory[p_id] = {'link': link, 'opc_a': opc_a, 'opc_b': opc_b}
            save_memory_wk()

            # Envio para o Telegram com DUPLA OPÇÃO
            msg = f"<b>🏷️ PLATAFORMA: WORKANA</b>\n"
            msg += f"<b>🏆 {nivel}</b> | 🕒 {date_text}\n\n"
            msg += f"<b>📂 Projeto:</b> <a href='{link}'>{title}</a>\n"
            msg += f"<b>💰 Orçamento:</b> {budget_str}\n\n"
            msg += f"<b>📋 RESUMO:</b>\n<i>{resumo}</i>\n\n"
            msg += f"<b>🛠 ARSENAL:</b>\n<code>{arsenal}</code>"

            # CRIAÇÃO DOS BOTÕES DE MÚLTIPLA ESCOLHA
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🎯 Opção A (Técnica)", callback_data=f"wk_A_{p_id}"))
            markup.add(InlineKeyboardButton("🤝 Opção B (Persuasiva)", callback_data=f"wk_B_{p_id}"))

            bot.send_message(CHAT_ID, msg, parse_mode="HTML", reply_markup=markup)

            seen_ids.append(p_id)
            save_seen(seen_ids)
            time.sleep(1)

        await browser.close()

if __name__ == "__main__":
    # Start Telegram Listener in separate thread
    t = threading.Thread(target=start_telegram_listener)
    t.daemon = True
    t.start()

    print("🤖 Jules V6.5.3 (Interactive Monitor) ONLINE")
    while True:
        try:
            asyncio.run(scan_workana())
        except Exception as e:
            print(f"⚠️ Erro no Radar: {e}")

        wait_time = random.randint(120, 300)
        print(f"💤 Trocando frequência em {wait_time}s...")
        time.sleep(wait_time)
