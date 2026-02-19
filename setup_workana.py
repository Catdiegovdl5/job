import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Conecta-se ao navegador que você abriu manualmente na porta 9222
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            # Usually the first context is the default one in a CDP session
            if not browser.contexts:
                 print("⚠️ Nenhum contexto encontrado. Tente abrir uma aba no Chrome.")
                 return
            
            context = browser.contexts[0]
            
            print("🛰️ Conectado ao navegador real!")
            
            # Salva o arquivo de autorização com os cookies do login que você acabou de fazer
            await context.storage_state(path="workana_auth.json")
            print("✅ SESSÃO CAPTURADA COM SUCESSO! O arquivo workana_auth.json foi gerado.")
            
            # Optional: Don't close the browser as it's the user's real browser
            # await browser.close() 
            
        except Exception as e:
            print(f"❌ Erro: Certifique-se de que o Chrome está aberto na porta 9222. Erro: {e}")

if __name__ == "__main__":
    asyncio.run(run())
