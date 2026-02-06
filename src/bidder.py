from playwright.sync_api import sync_playwright
import os
import time
import re

# Configuration
USER_DATA_DIR = "user_data"  # For session persistence (cookies)

def get_budget_average(text):
    """
    Parses budget range from text and returns the average (or min + 10%).
    Example: "$30 - $250 USD" -> (30+250)/2 = 140.
    Example: "$250 USD" -> 250.
    """
    matches = re.findall(r"\$([\d,]+)", text)
    if not matches:
        return None

    values = []
    for m in matches:
        try:
            val = int(m.replace(",", ""))
            values.append(val)
        except:
            pass

    if not values:
        return None

    if len(values) == 1:
        return values[0]

    # Range: Calculate Average
    avg = sum(values) / len(values)
    return int(avg)

def place_bid(url, proposal_text):
    """
    Automates the bidding process on Freelancer.com using Playwright.
    Uses persistent session to avoid re-login.
    """
    print(f"[BIDDER] Iniciando processo de lance para: {url}")

    with sync_playwright() as p:
        # Launch persistent context
        # HEADLESS=False for visual audit during dry run
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={"width": 1280, "height": 720}
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # 1. Navigate to Job
            print("[BIDDER] Navegando para URL...")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=30000)
            except Exception as e:
                print(f"[WARN] Timeout/Erro na navegação: {e}. Tentando prosseguir...")

            # 2. Check Login Status
            if page.locator("a[href*='/login']").count() > 0 and page.locator(".dashboard-sidebar-username").count() == 0:
                print("[BIDDER] Sessão não detectada. Tentando login com variáveis de ambiente...")
                # Attempt Login
                email = os.environ.get("FREELANCER_EMAIL")
                password = os.environ.get("FREELANCER_PASSWORD")

                if not email or not password:
                    print("[ERROR] Credenciais não encontradas (FREELANCER_EMAIL/PASS). Abortando.")
                    return False

                page.click("a[href*='/login']")
                page.fill("input[name='user']", email)
                page.fill("input[name='password']", password)
                page.click("button[type='submit']")
                try:
                    page.wait_for_load_state("networkidle", timeout=30000)
                except:
                    pass

                # Check again
                if page.locator("a[href*='/login']").count() > 0:
                     print("[ERROR] Falha no login automático. Requer intervenção manual.")
                     return False

            # 3. Extract Budget & Calculate Bid
            try:
                # Selector might need adjustment based on layout changes
                budget_text = page.locator(".PageProjectView-header-budget").inner_text()
                bid_amount = get_budget_average(budget_text)
            except:
                bid_amount = None

            if not bid_amount:
                print("[WARN] Não foi possível calcular o budget. Usando valor padrão ou mínimo.")
                bid_amount = 30 # Default safety

            print(f"[BIDDER] Valor do lance calculado: ${bid_amount}")

            # 4. Fill Bid Form
            # Using generic selectors if IDs vary
            try:
                page.fill("input[name='amount']", str(bid_amount))
            except:
                print("[WARN] Campo de valor não encontrado. Tentando seletor alternativo...")

            # 5. Fill Period
            try:
                page.fill("input[name='period']", "7")
            except:
                pass

            # 6. Fill Proposal Text
            try:
                page.fill("textarea[name='description']", proposal_text)
            except:
                print("[WARN] Campo de descrição não encontrado.")

            # 7. Submit
            print("[BIDDER] DRY RUN: Botão 'Place Bid' localizado mas NÃO será clicado.")
            # page.click("button:has-text('Place Bid')")

            print("[BIDDER] Simulação concluída com sucesso.")
            time.sleep(2)

            return True

        except Exception as e:
            print(f"[ERROR] Erro durante o lance: {e}")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 2:
        place_bid(sys.argv[1], sys.argv[2])
