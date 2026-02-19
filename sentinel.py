O conceito é: O seu PC vira o Servidor. O script fica rodando no seu computador (conectado ao Brave ou não), ouvindo o Telegram.

🛠️ Passo 1: Prepare o Terreno
Certifique-se de que você tem o Token do seu Bot no arquivo .env (variável TG_TOKEN).

Se não tiver, crie um bot no @BotFather no Telegram e pegue o token.

🛠️ Passo 2: O Código do "Telegram Sniper" (telegram_sniper.py)
Crie este arquivo novo. Ele mistura a tecnologia de Conexão com Brave (V19) com a Inteligência Llama 3.3, tudo via Telegram.

Python
import os
import sys
import time
import asyncio
import telebot
from telebot import types
from playwright.async_api import async_playwright
from sentinel_real import gerar_analise_diego
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID") # Opcional, para segurança

if not TG_TOKEN:
    print("❌ ERRO: TG_TOKEN não encontrado no .env")
    sys.exit(1)

bot = telebot.TeleBot(TG_TOKEN)

# --- MOTOR DE EXTRAÇÃO (Híbrido: Brave Remoto ou Headless) ---
async def extrair_dados_projeto(url):
    async with async_playwright() as p:
        browser = None
        # 1. Tenta conectar ao BRAVE aberto (Porta 9222)
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            print("🦁 Conectado ao Brave Local.")
        except:
            print("⚠️ Brave fechado. Tentando modo Headless com cookies...")
            # 2. Fallback: Abre navegador invisível com cookies salvos
            try:
                browser = await p.chromium.launch(headless=True)
                try:
                    context = await browser.new_context(storage_state="workana_auth.json")
                except:
                    context = await browser.new_context()
            except Exception as e:
                return None, f"Erro navegador: {e}", None

        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=40000)
            
            # Verifica Login
            if "login" in page.url and "workana.com" in page.url:
                 return None, "🔒 Bloqueio: Projeto Privado (Login necessário)", None

            # Seletores
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
                descricao = await page.locator("body").inner_text()
                descricao = descricao[:3000]

            orcamento = "A combinar"
            if await page.locator(budget_sel).count() > 0:
                orcamento = await page.locator(budget_sel).first.inner_text()

            await page.close() # Fecha aba, mantém browser
            if not browser.is_connected(): await browser.close()
            
            return titulo.strip(), descricao.strip(), orcamento.strip()
            
        except Exception as e:
            return None, f"Erro leitura: {e}", None

# --- HANDLERS DO TELEGRAM ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 **JULES ONLINE**\n\nEnvie um **LINK** da Workana ou **COLE O TEXTO** do projeto.\nEu vou gerar a proposta para você.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def processar_mensagem(message):
    entrada = message.text.strip()
    
    # Aviso de "Digitando..."
    msg_wait = bot.reply_to(message, "🧠 Processando inteligência...")
    
    titulo = ""
    descricao = ""
    orcamento = "A combinar"
    origem = "Texto Manual"

    # 1. DETECÇÃO: É LINK?
    if "http" in entrada:
        # Loop para rodar async dentro do sync
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Patch Windows
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        try:
            t, d, o = loop.run_until_complete(extrair_dados_projeto(entrada))
            if t:
                titulo = t
                descricao = d
                orcamento = o
                origem = "Link Extraído"
            else:
                bot.edit_message_text(f"❌ Falha ao ler link: {d}\n\nTente colar o texto manualmente.", message.chat.id, msg_wait.message_id)
                return
        except Exception as e:
            bot.edit_message_text(f"❌ Erro fatal no navegador: {e}", message.chat.id, msg_wait.message_id)
            return
        finally:
            loop.close()
    else:
        # É TEXTO MANUAL
        titulo = "Projeto Manual (Telegram)"
        descricao = entrada
        orcamento = "Não informado"

    # 2. GERAÇÃO (Llama 3.3)
    try:
        # Atualiza status
        bot.edit_message_text(f"📝 Escrevendo proposta para:\n*{titulo}*...", message.chat.id, msg_wait.message_id, parse_mode="Markdown")
        
        nivel, resumo, arsenal, opc_a, opc_b, val_sugerido, prazo = gerar_analise_diego(titulo, descricao, orcamento, 0)
        
        # 3. RESPOSTA FORMATADA (Fácil de Copiar)
        # Usamos <code> para clicar e copiar fácil no celular
        
        resposta = f"🚀 <b>{titulo}</b>\n"
        resposta += f"💰 {orcamento} -> Sugestão: {val_sugerido}\n"
        resposta += f"🏆 {nivel} | ⏱️ {prazo} dias\n\n"
        
        resposta += "👇 <b>TOQUE PARA COPIAR (OPÇÃO B)</b> 👇\n"
        resposta += f"<code>{opc_b}</code>\n\n"
        
        resposta += "👇 <b>TOQUE PARA COPIAR (OPÇÃO A)</b> 👇\n"
        resposta += f"<code>{opc_a}</code>"

        # Envia a resposta final
        bot.delete_message(message.chat.id, msg_wait.message_id)
        bot.send_message(message.chat.id, resposta, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(f"❌ Erro na IA: {e}", message.chat.id, msg_wait.message_id)

if __name__ == "__main__":
    print("🤖 TELEGRAM SNIPER ONLINE - Aguardando mensagens...")
    bot.infinity_polling()
🎮 Como Usar
No PC: Execute o script: python telegram_sniper.py.

Dica: Deixe o Brave aberto com o comando brave.exe --remote-debugging-port=9222 se quiser ler projetos privados.

No Celular (Telegram):

Abra a conversa com seu Bot.

Envie um Link: Cole o link da Workana e envie.

Envie um Texto: Copie a descrição do projeto e envie.

📲 O Resultado
O bot vai responder com uma mensagem formatada. As propostas estarão dentro de caixas cinzas (<code>). No Telegram do celular, basta tocar nessa caixa cinza e o texto é copiado automaticamente.

Aí é só ir no app da Workana (ou site mobile) e colar.