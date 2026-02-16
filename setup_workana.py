import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Manobra A: Perfil Persistente
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        print(f"📁 Usando perfil persistente em: {user_data_dir}")

        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        # Persistent context usually opens a page by default, but we can ensure we have one
        if context.pages:
            page = context.pages[0]
        else:
            page = await context.new_page()

        await page.goto("https://www.workana.com/login")

        print("🎯 AGUARDANDO LOGIN MANUAL...")
        print("Faça login na sua conta Workana e, quando estiver na Dashboard, volte aqui.")
        print("💡 DICA: Se o Google bloquear, use o login direto com e-mail e senha.")

        # O script fica pausado até você fechar o navegador
        await asyncio.sleep(300) # Você tem 5 minutos para logar

        # Salva o estado da sessão (cookies e login) para uso posterior (opcional se usar persistência, mas bom para backup)
        await context.storage_state(path="workana_auth.json")
        print("✅ SESSÃO CAPTURADA! O arquivo workana_auth.json foi gerado.")

        await context.close()

asyncio.run(run())
