import asyncio
from playwright.async_api import async_playwright

# Link de um projeto ativo (pode trocar por qualquer outro link real)
TARGET_URL = "https://www.workana.com/jobs" 

AUTH_FILE = "workana_auth.json"

async def raio_x_workana():
    async with async_playwright() as p:
        # Abre o navegador visível para você ver acontecendo
        browser = await p.chromium.launch(headless=False)
        
        try:
            context = await browser.new_context(storage_state=AUTH_FILE)
            print("✅ Login carregado.")
        except:
            print("⚠️ Sem login salvo. Criando sessão limpa...")
            context = await browser.new_context()

        page = await context.new_page()
        
        print("🕵️♂️ Infiltrando para extração de código...")
        
        # 1. Vai para a lista de projetos primeiro para garantir cookies
        try:
            await page.goto("https://www.workana.com/jobs", wait_until="networkidle", timeout=60000)
        except Exception as e:
             print(f"Erro ao carregar lista: {e}")
             await browser.close()
             return

        # 2. Pega o primeiro projeto da lista para usar de exemplo
        print("🔎 Selecionando um alvo aleatório para análise...")
        try:
            # Tenta clicar no primeiro titulo de projeto
            await page.click(".project-item .project-title a")
        except:
            print("⚠️ Seletor .project-item falhou, tentando generico...")
            try:
                await page.click("h2.h3 a")
            except Exception as e:
                print(f"❌ Falha ao selecionar projeto: {e}")
                
        await page.wait_for_load_state("domcontentloaded")
        print("✅ Página do projeto carregada.")

        # 2.5 CLICA NO BOTÃO DE PROPOSTA PARA IR AO FORMULÁRIO
        
        # LIMPEZA VISUAL (CRÍTICO PARA CLICAR)
        try:
            await page.add_style_tag(content="""
                #onetrust-banner-sdk, #workanaChat, .header-user, .navbar-collapse, #intercom-container, footer, .drift-widget-container { 
                    display: none !important; 
                    pointer-events: none !important;
                }
            """)
            print("🧹 Limpeza visual realizada (Cookie banner e chat removidos).")
        except: pass

        print("🖱️ Clicando em 'Fazer uma proposta' para revelar o formulário...")
        try:
            # Tenta primeiro o ID, depois o texto
            button_selector = '#bid_button, a.btn-primary:has-text("Fazer uma proposta")'
            
            if await page.is_visible(button_selector):
                print("✅ Botão visível. Clicando com force=True...")
                await page.click(button_selector, force=True)
            else:
                print("⚠️ Botão de proposta não visível pelo seletor. Tentando JS...")
                await page.evaluate("document.querySelector('a.btn-primary').click()")
                
            # Espera a navegação ou o modal
            print("⏳ Aguardando campos do formulário...")
            try:
                # Espera aparecer o campo de valor ou descrição
                await page.wait_for_selector('input[name="amount"], #BidAmount, textarea[name="description"]', timeout=30000)
                print("✅ Formulário de proposta aberto e detectado!")
            except:
                print("⚠️ Timeout: Formulário pode não ter aberto corretamente (ou seletor mudou).")
                
        except Exception as e:
            print(f"❌ Erro ao clicar no botão de proposta: {e}")

        print("📸 Tirando Radiografia da página de TAREFA (FORMULÁRIO)...")
        
        # 3. EXTRAÇÃO DO CÓDIGO HTML COMPLETO
        html_content = await page.content()
        
        # Salva o "Mapa" em um arquivo
        with open("workana_form_mapa.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print("✅ CÓDIGO EXTRAÍDO: 'workana_form_mapa.html'")
        
        # 4. Tira um print para compararmos visualmente
        try:
            await page.screenshot(path="workana_form_print.png", full_page=True)
            print("📸 FOTO TIRADA: 'workana_form_print.png'")
        except:
             print("⚠️ Erro ao tirar print full page.")
        
        print("🛑 O navegador ficará aberto por 60s para você inspecionar manualmente se quiser.")
        await asyncio.sleep(60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(raio_x_workana())
