import sys
import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("FLN_USER")
PASSWORD = os.getenv("FLN_PASS")

def main():
    if len(sys.argv) < 2: return
    filepath = sys.argv[1]
    
    # Lê a proposta
    with open(filepath, 'r') as f: content = f.read()
    proposal_text = content.split('---')[-1].strip()
    
    print(f"🚀 Iniciando disparo para: {os.path.basename(filepath)}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.freelancer.com/login")
        
        # Simulação de Login
        if page.is_visible('input[name="user"]'):
            page.fill('input[name="user"]', EMAIL or "usuario_teste")
            if PASSWORD: page.fill('input[name="passwd"]', PASSWORD)
        
        print("✅ Navegador Aberto. (Modo Simulação Ativo)")
        time.sleep(10) # Tempo para ver o resultado
        browser.close()

if __name__ == "__main__":
    main()
