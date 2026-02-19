import os
import sys
import time
import asyncio
import subprocess
import telebot
from telebot import types
from playwright.async_api import async_playwright
from sentinel_real import gerar_analise_diego
from dotenv import load_dotenv

load_dotenv()
TG_TOKEN = os.environ.get("TG_TOKEN")

if not TG_TOKEN:
    print("❌ ERRO: TG_TOKEN não encontrado no .env")
    sys.exit(1)

bot = telebot.TeleBot(TG_TOKEN)

# Armazena dados temporários para o botão funcionar
temp_memory = {}

async def extrair_dados_projeto(url):
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            print("🦁 Conectado ao Brave.")
        except:
            print("⚠️ Brave fechado. Tentando Headless...")
            try:
                browser = await p.chromium.launch(headless=True)
                try:
                    auth_path = os.path.abspath("workana_auth.json")
                    if os.path.exists(auth_path):
                        context = await browser.new_context(storage_state=auth_path)
                    else:
                        context = await browser.new_context()
                except:
                    context = await browser.new_context()
            except Exception as e:
                return None, f"Erro Navegador: {e}", None

        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=40000)
            
            if "login" in page.url and "workana.com" in page.url:
                return None, "🔒 Bloqueio: Login necessário", None

            title_sel = "h1.title, .project-title"
            desc_sel = ".project-details, .expander"
            budget_sel = ".budget .values"
            
            titulo = "Sem Título"
            if await page.locator(title_sel).count() > 0:
                titulo = await page.locator(title_sel).first.inner_text()
            
            descricao = ""
            if await page.locator(desc_sel).count() > 0:
                descricao = await page.locator(desc_sel).first.inner_text()
            else:
                try:
                    descricao = await page.locator("body").inner_text()
                    descricao = descricao[:3000]
                except: pass

            orcamento = "A combinar"
            if await page.locator(budget_sel).count() > 0:
                orcamento = await page.locator(budget_sel).first.inner_text()

            await page.close()
            return titulo.strip(), descricao.strip(), orcamento.strip()
        except Exception as e:
            return None, f"Erro Leitura: {e}", None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 **DIEGO SNIPER ONLINE**\nMande o LINK ou COLE O TEXTO do projeto.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def processar_mensagem(message):
    entrada = message.text.strip()
    msg_wait = bot.reply_to(message, "🧠 Diego AI analisando...")
    
    titulo = "Projeto Manual"
    descricao = entrada
    orcamento = "A combinar"
    link_projeto = ""

    if "http" in entrada:
        link_projeto = entrada
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            t, d, o = loop.run_until_complete(extrair_dados_projeto(entrada))
            if t:
                titulo, descricao, orcamento = t, d, o
            else:
                bot.edit_message_text(f"❌ Falha: {d}\n\nCole o texto manualmente.", message.chat.id, msg_wait.message_id)
                loop.close()
                return
            loop.close()
        except Exception as e:
            bot.edit_message_text(f"❌ Erro fatal: {e}", message.chat.id, msg_wait.message_id)
            return
    else:
        titulo = "Projeto Manual"
        descricao = entrada
        orcamento = "Não informado"

    try:
        bot.edit_message_text(f"📝 Gerando estratégia para:\n*{titulo}*...", message.chat.id, msg_wait.message_id, parse_mode="Markdown")
        
        nivel, resumo, arsenal, opc_a, opc_b, val_sugerido, prazo = gerar_analise_diego(titulo, descricao, orcamento, 0)
        
        # Salva na memória para o botão funcionar
        msg_id = message.message_id
        temp_memory[msg_id] = {
            "link": link_projeto,
            "texto": opc_b,
            "preco": "50",
            "prazo": prazo
        }

        # BOTOES
        markup = types.InlineKeyboardMarkup()
        if link_projeto:
            btn_disparar = types.InlineKeyboardButton("🚀 DISPARAR AGORA", callback_data=f"send_{msg_id}")
            markup.add(btn_disparar)

        # --- SPLIT FIRE (3 Mensagens) ---
        bot.delete_message(message.chat.id, msg_wait.message_id)
        
        # 1. Info Header
        info_msg = f"🚀 <b>{titulo}</b>\n"
        info_msg += f"💰 {orcamento}\n"
        info_msg += f"🏆 {nivel} | ⏱️ {prazo} dias"
        bot.send_message(message.chat.id, info_msg, parse_mode="HTML")

        # 2. Opção B (Persuasiva)
        time.sleep(0.5)
        bot.send_message(message.chat.id, "👇 <b>OPÇÃO B (Persuasiva)</b>", parse_mode="HTML")
        bot.send_message(message.chat.id, f"<code>{opc_b}</code>", parse_mode="HTML", reply_markup=markup if link_projeto else None)
        
        # 3. Opção A (Direta)
        time.sleep(0.5)
        bot.send_message(message.chat.id, "👇 <b>OPÇÃO A (Direta)</b>", parse_mode="HTML")
        bot.send_message(message.chat.id, f"<code>{opc_a}</code>", parse_mode="HTML")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Erro na IA: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("send_"))
def callback_disparo(call):
    msg_id = int(call.data.split("_")[1])
    dados = temp_memory.get(msg_id)
    
    if not dados:
        bot.answer_callback_query(call.id, "❌ Dados expirados.")
        return

    bot.answer_callback_query(call.id, "🚀 Iniciando executor...")
    bot.send_message(call.message.chat.id, "⚡ <b>EXECUTANDO ENVIO AUTOMÁTICO...</b>", parse_mode="HTML")
    
    # CHAMA O EXECUTOR
    subprocess.Popen([
        sys.executable, 
        'executor_sniper.py', 
        dados['link'], 
        dados['texto'], 
        dados['preco'], 
        dados['prazo']
    ])

if __name__ == "__main__":
    print("🤖 DIEGO SNIPER ONLINE...")
    bot.infinity_polling()
