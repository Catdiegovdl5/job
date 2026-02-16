import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Cria uma pasta para salvar seu perfil real de navegação
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")

        # Lança o navegador com camuflagem (Persistent Context)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False, # Abre a janela para você logar
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        page = context.pages[0]
        await page.goto("https://www.workana.com/login")

        print("🎯 OPERAÇÃO STEALTH: Navegador pronto.")
        print("1. Tente logar com E-MAIL E SENHA direto na Workana (Evite o botão Google).")
        print("2. Se precisar usar o Google, faça o login agora.")
        print("3. Quando estiver logado na Dashboard, volte ao terminal.")

        # Aguarda 5 minutos para você completar a missão
        await asyncio.sleep(300)

        # Salva a autorização final
        await context.storage_state(path="workana_auth.json")
        print("✅ SESSÃO CAPTURADA! Arquivo workana_auth.json gerado com sucesso.")
        await context.close()

if __name__ == "__main__":
    asyncio.run(run())
