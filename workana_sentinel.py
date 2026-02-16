import asyncio
import json
import os
import time
import random
import re
import telebot
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

def load_seen():
    if os.path.exists(SEEN_PROJECTS_FILE):
        try:
            with open(SEEN_PROJECTS_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_seen(seen):
    with open(SEEN_PROJECTS_FILE, "w") as f: json.dump(seen, f)

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

            # ⚓ NOVA LÓGICA DE ID: Busca o link e extrai o ID dele
            link_el = await p_item.query_selector(".project-title a")
            href = await link_el.get_attribute("href") if link_el else ""

            # O ID agora é extraído da URL do projeto
            # Exemplo: /job/123456-titulo-do-projeto -> 123456-titulo-do-projeto (ou só o número se preferir, mas href todo é unico)
            # Vamos pegar o último segmento para ser consistente com a logica sugerida: href.split('/')[-1]
            p_id = href.split('/')[-1] if href else None

            date_el = await p_item.query_selector(".date")
            date_text = (await date_el.inner_text()).lower() if date_el else "data n/a"

            # LOG DE DIAGNÓSTICO NO TERMINAL
            print(f"--- Verificando: {title[:25]}... | ID: {p_id} | Data: {date_text}")

            if not p_id:
                print("   ⏭️ Ignorado: Não foi possível extrair ID do link.")
                continue

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

            # SE CHEGOU AQUI, O ALVO É QUENTE!
            print(f"   🎯 ALVO APROVADO: {title}")

            desc_el = await p_item.query_selector(".project-details")
            desc = (await desc_el.inner_text()).strip() if desc_el else "Sem Descrição"

            budget_el = await p_item.query_selector(".budget")
            budget_str = (await budget_el.inner_text()).strip() if budget_el else "N/A"

            link = "https://www.workana.com" + href

            # Diego analisa o alvo
            nivel, resumo, ferramentas, proposta = gerar_analise_diego(title, desc, budget_str, 50.0)

            # Envio para o Telegram
            msg = f"<b>🏷️ PLATAFORMA: WORKANA</b>\n"
            msg += f"<b>🏆 {nivel}</b> | 🕒 {date_text}\n\n"
            msg += f"<b>📂 Projeto:</b> <a href='{link}'>{title}</a>\n"
            msg += f"<b>💰 Orçamento:</b> {budget_str}\n\n"
            msg += f"<b>📋 RESUMO:</b>\n<i>{resumo}</i>\n\n"
            msg += f"<b>🛠 ARSENAL:</b>\n<code>{ferramentas}</code>\n\n"
            msg += f"<b>💡 PROPOSTA:</b>\n{proposta}"

            bot.send_message(CHAT_ID, msg, parse_mode="HTML")

            seen_ids.append(p_id)
            save_seen(seen_ids)
            time.sleep(1)

        await browser.close()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(scan_workana())
        except Exception as e:
            print(f"⚠️ Erro no Radar: {e}")

        wait_time = random.randint(120, 300) # Frequência aumentada
        print(f"💤 Trocando frequência em {wait_time}s...")
        time.sleep(wait_time)
