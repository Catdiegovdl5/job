import sys
import asyncio
import time
import pyautogui
import pyperclip
from playwright.async_api import async_playwright

async def missao_automatica(link, texto, preco, prazo):
    print(f"🔧 Iniciando Automação: {link}")
    
    async with async_playwright() as p:
        # Tenta conectar ao Brave já aberto (Mais rápido e seguro)
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            print("🦁 Conectado ao Brave.")
        except:
            # Fallback: Abre novo
            print("⚠️ Brave não encontrado. Abrindo navegador novo...")
            browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
            try:
                context = await browser.new_context(storage_state="workana_auth.json")
            except:
                context = await browser.new_context()

        page = await context.new_page()
        await page.goto(link, wait_until="domcontentloaded", timeout=60000)
        
        # Traz janela para frente
        try:
            await page.bring_to_front()
            time.sleep(1)
        except: pass

        # 1. Clicar em "Fazer Proposta"
        try:
            print("🖱️ Buscando botão 'Fazer Proposta'...")
            # Tenta clicar via JS para garantir
            await page.evaluate("document.querySelector('a.btn-primary').click()")
            print("✅ Botão encontrado via JS.")
        except:
            try:
                print("⚠️ Botão não achado via JS, tentando visual...")
                await page.click("text=Fazer uma proposta")
                print("✅ Botão encontrado via texto.")
            except:
                print("❌ Botão 'Fazer Proposta' não encontrado. Verifique a página.")

        time.sleep(3)

        # 2. Preencher Valor
        try:
            print(f"💰 Preenchendo valor: {preco}")
            await page.fill('input[name="amount"]', str(preco))
        except Exception as e:
            print(f"⚠️ Não conseguiu preencher valor: {e}")

        # 3. Colar Texto (Simulando Humano)
        try:
            print("📝 Colando proposta...")
            await page.click('textarea[name="description"]')
            time.sleep(0.5)
            pyperclip.copy(texto)
            # Cola com Ctrl+V real
            pyautogui.hotkey('ctrl', 'v')
            print("✅ Proposta colada!")
        except:
            try:
                # Fallback: fill direto
                await page.fill('textarea[name="description"]', texto)
                print("✅ Proposta preenchida (fallback).")
            except Exception as e:
                print(f"❌ Erro ao colar proposta: {e}")

        print("\n" + "="*40)
        print("✅ PRONTO! Revise e clique em ENVIAR manualmente.")
        print("="*40)
        # Deixamos aberto para você clicar no botão final (Segurança)
        await asyncio.sleep(600)

if __name__ == "__main__":
    # Recebe argumentos do telegram_sniper.py
    if len(sys.argv) > 4:
        link = sys.argv[1]
        texto = sys.argv[2]
        preco = sys.argv[3]
        prazo = sys.argv[4]
        
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(missao_automatica(link, texto, preco, prazo))
    else:
        print("❌ Uso: python executor_sniper.py <link> <texto> <preco> <prazo>")
