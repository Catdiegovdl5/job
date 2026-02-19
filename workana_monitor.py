import asyncio
import sys
import json
import os
import time
import random
import re
import pyautogui
import pygetwindow as gw
import pyperclip
import subprocess
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import hashlib

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

async def disparar_proposta_workana(project_link, proposal_text, preco, prazo):
    """
    Módulo de Lance Automático para Workana (V9.2 - Protocolo Mãos de Ferro/Foco + Colagem).
    """
    async with async_playwright() as p:
        # 1. ABRE O CHROME EM MODO MAXIMIZADO
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        try:
            # Tenta carregar cookies
            try:
                context = await browser.new_context(storage_state=AUTH_FILE)
            except:
                context = await browser.new_context()
                
            page = await context.new_page()
            print(f"📡 Infiltrando: {project_link}")
            
            await page.goto(project_link, wait_until="networkidle", timeout=60000)
            
            # ⚓ GARANTE O FOCO DA JANELA (Protocolo V9.2)
            try:
                # Tenta trazer a janela do Chrome para a frente
                # Buscamos janelas com 'Workana' ou 'Google Chrome' ou 'Chromium' no título
                # Mas como estamos no playwright headless=False, o título da janela costuma ser o título da página
                chrome_windows = gw.getWindowsWithTitle('Workana') + gw.getWindowsWithTitle('Chrome') + gw.getWindowsWithTitle('Chromium')
                if chrome_windows:
                    chrome_windows[0].activate()
                    print("📺 Janela do Chrome focada e ativa.")
            except Exception as e:
                print(f"⚠️ Não foi possível forçar o foco da janela: {e}")

            time.sleep(3)

            # 2. LOCALIZAÇÃO E CLIQUE NO BOTÃO ROXO
            try:
                btn = await page.wait_for_selector("text='Fazer uma proposta'", timeout=15000)
                if btn:
                    box = await btn.bounding_box()
                    if box:
                        # O +80 compensa a barra de ferramentas do navegador (Ajuste empírico)
                        x_pos = box['x'] + (box['width']/2)
                        y_pos = box['y'] + (box['height']/2) + 80
                        pyautogui.click(x_pos, y_pos)
                        print(f"🖱️ Clique físico executado em ({x_pos}, {y_pos}).")
                    else:
                        print("⚠️ Botão sem caixa delimitadora, tentando clique via Playwright force...")
                        await btn.click(force=True)
            except Exception as e:
                print(f"⚠️ Erro ao clicar no botão: {e}")
            
            # 🕒 Pausa humana para o formulário carregar
            time.sleep(5)

            # 2.1 PREENCHER PREÇO
            try:
                price_selectors = ['input[name="amount"]', '#BidAmount', 'input[name="hourly_rate"]', '.bid-amount-input input']
                for selector in price_selectors:
                    field = await page.query_selector(selector)
                    if field and await field.is_visible():
                        await field.click(force=True)
                        await field.fill(str(preco).replace(',', '.'))
                        print(f"💰 Preço preenchido: {preco}")
                        break
            except: pass

            # 3. DIGITAÇÃO VIA ÁREA DE TRANSFERÊNCIA (Mais rápido e seguro)
            try:
                textarea = await page.wait_for_selector('textarea[name="description"], #BidDescription, .bid-description-input textarea', timeout=15000)
                if textarea:
                    # Tenta clicar no centro do textarea usando coordenadas se possível, ou click force do playwright
                    box_text = await textarea.bounding_box()
                    if box_text:
                        # Clica fisicamente para garantir foco do SO
                        pyautogui.click(box_text['x'] + 50, box_text['y'] + 50 + 80)
                    else:
                         await textarea.click(force=True)
                    
                    # PROTOCOLO DE COLAGEM FANTASMA
                    pyperclip.copy(proposal_text) # Copia o texto para o Windows
                    time.sleep(0.5)
                    pyautogui.hotkey('ctrl', 'v') # Cola fisicamente o texto
                    print("✅ PROPOSTA COLADA PELO TECLADO DO WINDOWS!")
            except Exception as e:
                print(f"❌ Erro na digitação/colagem: {e}")
            
            # 4. PREENCHER PRAZO
            try:
                 duration_input = await page.wait_for_selector('input[name="duration"], select[name="duration"]', timeout=3000)
                 if duration_input:
                     await duration_input.fill(str(prazo))
            except: pass

            print("🏁 Sniper pronto. Janela aberta por 10 minutos para sua revisão.")
            await asyncio.sleep(600) 

        except Exception as e:
            print(f"❌ Falha no disparo: {e}")
        finally:
            try:
                await browser.close()
            except: pass
            


@bot.callback_query_handler(func=lambda call: call.data.startswith("wk_"))
def handle_workana_bid(call):
    # Formato: wk_OPCAO_ID (ex: wk_A_a1b2c3d4e5)
    try:
        parts = call.data.split("_")
        if len(parts) < 3: return
        opcao = parts[1]
        p_id = "_".join(parts[2:])
        
        project_data = memory.get(p_id)
        if not project_data:
            bot.answer_callback_query(call.id, "❌ Dados expirados.")
            return

        prop_text = project_data.get('opc_a') if opcao == "A" else project_data.get('opc_b')
        preco = project_data.get('orcamento', '50')
        prazo = project_data.get('prazo', '7')
        
        bot.answer_callback_query(call.id, f"🚀 Iniciando Executor...")
        bot.send_message(CHAT_ID, f"🚀 <b>BRAÇO MECÂNICO ATIVADO!</b>\nO executor independente foi lançado para o projeto.\nPreço: {preco} | Prazo: {prazo}\n(Preencha valor e prazo manualmente se necessário)", parse_mode="HTML")
        
        # DISPARO COM ARGUMENTOS COMPLETOS (V12.0)
        subprocess.Popen([
            sys.executable, 
            'executor_sniper.py', 
            project_data['link'], 
            prop_text,
            str(preco),
            str(prazo)
        ])
        
    except Exception as e:
        print(f"Erro no handler: {e}")
        bot.send_message(CHAT_ID, f"❌ Erro ao lançar executor: {e}")


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
        
        for p_item in projects[:15]: # Reduzido para 15 para ser menos agressivo
            title_el = await p_item.query_selector(".project-title")
            title = (await title_el.inner_text()).strip() if title_el else "Sem Título"
            
            link_el = await p_item.query_selector(".project-title a")
            href = await link_el.get_attribute("href") if link_el else ""
            
            # ⚓ HASHING TÁTICO (V7.5): Transforma o link longo em um ID de 10 letras
            # Isso resolve o erro 400 BUTTON_DATA_INVALID definitivamente
            p_id = hashlib.md5(href.encode()).hexdigest()[:10]
            
            date_el = await p_item.query_selector(".date")
            date_text = (await date_el.inner_text()).lower() if date_el else "agora mesmo"
            
            print(f"--- Verificando: {title[:25]}... | ID Seguro: {p_id} | Data: {date_text}")

            if p_id in seen_ids:
                print(f"   ⏭️ Ignorado: Já enviado.")
                continue

            # FILTRO DE 3 DIAS (Mantido)


            # FILTRO DE DATA V8.3 (Corrigido)
            is_too_old = False
            if any(x in date_text for x in ["semana", "mês", "mes", "ano"]):
                is_too_old = True
            elif "dia" in date_text:
                days = re.findall(r'\d+', date_text)
                if days and int(days[0]) > 3:
                    is_too_old = True
            
            # Se for "agora mesmo" ou "há X minutos", is_too_old continuará False.

            if is_too_old:
                print(f"   ⏭️ Ignorado: Antigo ({date_text})")
                continue
            
            print(f"   🎯 ALVO APROVADO: {title}")
            
            # 🕒 PAUSA ANTI-BAN (Simula tempo de leitura do projeto)
            wait_time = random.randint(5, 12)
            print(f"   ⏳ Processando... ({wait_time}s)")
            await asyncio.sleep(wait_time) 

            desc_el = await p_item.query_selector(".project-details")
            desc = (await desc_el.inner_text()).strip() if desc_el else "Sem Descrição"
            
            budget_el = await p_item.query_selector(".budget")
            budget_str = (await budget_el.inner_text()).strip() if budget_el else "N/A"

            # 🧠 GERAÇÃO DA PROPOSTA (Llama 3.3)
            nivel, resumo, arsenal, opc_a, opc_b, orcamento, prazo = gerar_analise_diego(title, desc, budget_str, 50.0)
            
            link = "https://www.workana.com" + href
            
            # =================================================================
            # 👇 AQUI ESTÁ A MUDANÇA: IMPRESSÃO DIRETA NO SEU TERMINAL 👇
            # =================================================================
            print("\n" + "█"*50)
            print(f"🚀 PROJETO ENCONTRADO: {title}")
            print(f"🔗 LINK: {link}")
            print("-" * 50)
            print(f"💰 Orçamento: {orcamento} | Prazo: {prazo} dias")
            print("-" * 50)
            print("📝 PROPOSTA RECOMENDADA (OPÇÃO B - Persuasiva):")
            print("-" * 20)
            print(opc_b)
            print("-" * 20)
            print("📝 PROPOSTA TÉCNICA (OPÇÃO A - Direta):")
            print("-" * 20)
            print(opc_a)
            print("█"*50 + "\n")
            # =================================================================
            
            # Guarda os dados na memória usando o NOVO KEY (HASH)
            memory[p_id] = {
                'link': link, 
                'opc_a': opc_a, 
                'opc_b': opc_b,
                'orcamento': orcamento,
                'prazo': prazo
            }
            save_memory_wk()

            # Envio para o Telegram com ID Compacto
            msg = f"<b>🏷️ WORKANA | {nivel}</b>\n🕒 {date_text}\n\n"
            msg += f"<b>📂 Projeto:</b> <a href='{link}'>{title}</a>\n"
            msg += f"<b>💰 Orçamento:</b> {budget_str}\n\n"
            msg += f"<b>📋 RESUMO:</b>\n<i>{resumo}</i>\n\n"
            msg += f"<b>🛠 ARSENAL:</b>\n<code>{arsenal}</code>"

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🎯 Opção A", callback_data=f"wk_A_{p_id}"))
            markup.add(InlineKeyboardButton("🤝 Opção B", callback_data=f"wk_B_{p_id}"))
            
            try:
                bot.send_message(CHAT_ID, msg, parse_mode="HTML", reply_markup=markup)
            except Exception as e:
                print(f"❌ Erro ao enviar Telegram: {e}")
            
            seen_ids.append(p_id)
            save_seen(seen_ids)
            
            # 🕒 ESPAÇAMENTO ENTRE ENVIOS
            print("   💤 Descanso tático entre envios...")
            await asyncio.sleep(random.randint(10, 20))

        await browser.close()

if __name__ == "__main__":
    # Start Telegram Listener in separate thread
    t = threading.Thread(target=start_telegram_listener)
    t.daemon = True
    t.start()
    
    print("🤖 Jules V6.5.3 (Interactive Monitor - Fixed) ONLINE")
    while True:
        try:
            asyncio.run(scan_workana())
        except Exception as e:
            print(f"⚠️ Erro no Radar: {e}")
        
        wait_time = random.randint(120, 300)
        print(f"💤 Trocando frequência em {wait_time}s...")
        time.sleep(wait_time)
