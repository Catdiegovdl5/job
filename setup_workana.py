import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Abre o navegador visível para você fazer login
        browser = await p.chromium.launch(headless=False)
        # Cria um contexto que salvará seus dados na pasta 'workana_data'
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        page = await context.new_page()
        await page.goto("https://www.workana.com/login")

        print("🎯 AGUARDANDO LOGIN MANUAL...")
        print("Faça login na sua conta Workana e, quando estiver na Dashboard, volte aqui.")

        # O script fica pausado até você fechar o navegador
        await asyncio.sleep(300) # Você tem 5 minutos para logar

        # Salva o estado da sessão (cookies e login)
        await context.storage_state(path="workana_auth.json")
        print("✅ SESSÃO CAPTURADA! O arquivo workana_auth.json foi gerado.")
        await browser.close()

asyncio.run(run())
