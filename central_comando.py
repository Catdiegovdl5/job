import os
import time
import sys
import asyncio
import pyautogui
import pyperclip
from playwright.async_api import async_playwright
from sentinel_real import gerar_analise_diego

# Tenta importar BeautifulSoup (Opcional)
try:
    from bs4 import BeautifulSoup
except: BeautifulSoup = None

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

async def connect_to_browser(playwright_instance):
    """Tenta conectar ao navegador na porta de depuração."""
    try:
        # Tenta conectar na porta padrão 9222
        browser = await playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
        return browser
    except Exception as e:
        print(f"❌ Erro ao conectar na porta 9222: {e}")
        return None

async def extrair_dados_projeto(url):
    print(f"\n🕵️♂️ CONECTANDO AO BRAVE (SESSÃO ATIVA): {url}")
    print("⏳ Aguarde...")
    
    async with async_playwright() as p:
        browser = await connect_to_browser(p)
        
        if not browser:
            print("⚠️ CERTIFIQUE-SE DE QUE O BRAVE FOI ABERTO COM A PORTA 9222!")
            print("Comando: brave.exe --remote-debugging-port=9222")
            return None, None, None

        try:
            # Usa o contexto padrão (sua sessão logada)
            if not browser.contexts:
                 context = await browser.new_context()
            else:
                 context = browser.contexts[0]
            
            # Abre uma nova aba (para não atrapalhar o que você está fazendo)
            page = await context.new_page()
            
            try:
                # Aumenta timeout para 60s
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Seletores Workana
                title_sel = "h1.title, .project-title"
                desc_sel = ".project-details, .expander"
                budget_sel = ".budget .values"
                
                # Extração
                titulo = "Título não detectado (Página carregou?)"
                if await page.locator(title_sel).count() > 0:
                    titulo = await page.locator(title_sel).first.inner_text()

                descricao = "Descrição não detectada"
                if await page.locator(desc_sel).count() > 0:
                    descricao = await page.locator(desc_sel).first.inner_text()
                else:
                    try:
                        # Tenta pegar todo texto visível se falhar
                        descricao = await page.locator("body").inner_text()
                        descricao = descricao[:3000] # Limite para IA
                    except: pass

                orcamento = "A combinar"
                if await page.locator(budget_sel).count() > 0:
                    orcamento = await page.locator(budget_sel).first.inner_text()

                print("✅ DADOS EXTRAÍDOS DA SUA SESSÃO!")
                return titulo.strip(), descricao.strip(), orcamento.strip()
                
            except Exception as e:
                print(f"❌ Erro na leitura da página: {e}")
                return None, None, None
            finally:
                # Fecha apenas a aba do robô, não o navegador inteiro
                await page.close()
                await browser.close()
                
        except Exception as e:
            print(f"❌ FALHA DE CONEXÃO OU EXECUÇÃO: {e}")
            return None, None, None

async def menu_principal():
    limpar_tela()
    print("🦁 JULES V19.0 - MODO BRAVE REMOTO")
    print("===============================================")
    print("👉 Opção A: Cole o Link e dê ENTER.")
    print("👉 Opção B: Dê ENTER vazio para ler o Clipboard.")
    print("===============================================")
    
    try:
        loop = asyncio.get_event_loop()
        entrada = await loop.run_in_executor(None, input, ">> ")
        entrada = entrada.strip()
    except: return

    if not entrada:
        print("📋 Lendo Área de Transferência...")
        entrada = pyperclip.paste().strip()
        if not entrada:
            print("❌ Clipboard vazio!")
            time.sleep(1)
            await menu_principal()
            return
        print(f"🔗 Detectado: {entrada[:60]}...")

    titulo = ""
    descricao = ""
    orcamento = "A combinar"

    if entrada.startswith("http"):
        # MODO LINK (CONECTADO AO BRAVE)
        titulo_res, descricao_res, orcamento_res = await extrair_dados_projeto(entrada)
        
        if not titulo_res or "não detectado" in titulo_res:
            print("\n⚠️ O robô não conseguiu ler o título.")
            print("Verifique se o link está correto ou se a página exige login (você está logado no Brave?)")
            
            loop = asyncio.get_event_loop()
            escolha = await loop.run_in_executor(None, input, "Deseja inserir TEXTO manualmente? (s/n): ")
            
            if escolha.lower() == 's':
                print("Cole o Título e Descrição, dê Enter, Ctrl+Z e Enter:")
                loop = asyncio.get_event_loop()
                descricao = await loop.run_in_executor(None, sys.stdin.read)
                descricao = descricao.strip()
                titulo = "Projeto Manual"
            else:
                return await menu_principal()
        else:
             titulo, descricao, orcamento = titulo_res, descricao_res, orcamento_res
    else:
        # MODO TEXTO
        titulo = "Projeto Manual"
        descricao = entrada
        orcamento = "Não informado"

    print("\n🧠 PROCESSANDO ESTRATÉGIA (Llama 3.3)...")
    
    loop = asyncio.get_event_loop()
    nivel, resumo, arsenal, opc_a, opc_b, val_sugerido, prazo = await loop.run_in_executor(None, gerar_analise_diego, titulo, descricao, orcamento, 0)

    limpar_tela()
    print(f"🚀 PROJETO: {titulo}")
    print(f"💰 Budget: {orcamento}")
    print(f"🏆 Nível: {nivel} | ⏱️ Prazo: {prazo} dias")
    print("===============================================")
    print("📝 PROPOSTA PERSUASIVA (OPÇÃO B):")
    print(opc_b)
    print("===============================================")
    
    print("\n[1] Copiar Opção B")
    print("[2] Copiar Opção A")
    print("[3] Digitar Automaticamente")
    print("[0] Nova Consulta")
    print("[x] Sair")
    
    # Reset do stdin para input funcionando no Windows
    try:
        if sys.platform == 'win32':
             sys.stdin = open('CON', 'r')
    except: pass
    
    escolha = await loop.run_in_executor(None, input, "\nEscolha: ")

    if escolha == '1':
        pyperclip.copy(opc_b)
        print("✅ Copiado!")
        time.sleep(1)
    elif escolha == '2':
        pyperclip.copy(opc_a)
        print("✅ Copiado!")
        time.sleep(1)
    elif escolha == '3':
        print("\n⚠️ Clique no campo da Workana em 5 segundos...")
        for i in range(5, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)
        print("\n🔥 Digitando...")
        lines = opc_b.split('\n')
        for line in lines:
            pyautogui.write(line)
            pyautogui.press('enter')
            time.sleep(0.05)
            
    if escolha.lower() == 'x':
        return
        
    await menu_principal()

def main_sync():
    # PATCH WINDOWS
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        asyncio.run(menu_principal())
    except KeyboardInterrupt:
        print("\nSaindo...")

if __name__ == "__main__":
    main_sync()
