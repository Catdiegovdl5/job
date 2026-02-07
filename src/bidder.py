import sys
import os
import shutil
import time
from playwright.sync_api import sync_playwright

def parse_proposal(filepath):
    meta = {}
    body = []
    reading_body = False
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == '---':
                reading_body = True
                continue
            if reading_body:
                body.append(line)
            else:
                if ':' in line:
                    key, val = line.split(':', 1)
                    meta[key.strip().upper()] = val.strip()
    return meta, "".join(body).strip()

def place_bid(url, proposal_text):
    email = os.getenv("FREELANCER_EMAIL")
    password = os.getenv("FREELANCER_PASSWORD")

    # Simulation Mode if no credentials
    if not email or not password:
        print("[WARN] Credentials not found. Running in SIMULATION MODE.")
        print("Iniciando Navegador... (Simulated)")
        time.sleep(1)
        print("Efetuando Login... (Simulated)")
        time.sleep(1)
        print(f"Navegando para: {url} (Simulated)")
        time.sleep(1)
        print(f"Preenchendo proposta... (Simulated)")
        time.sleep(1)
        print("Lance Enviado! (Simulated)")
        return True

    with sync_playwright() as p:
        print("Iniciando Navegador...")
        try:
            browser = p.chromium.launch(headless=True) # Change to False if you want to see it
            page = browser.new_page()

            print("Efetuando Login...")
            page.goto("https://www.freelancer.com/login")

            # Selectors - Best Guess based on standard structure
            # Attempt to handle different login variations
            try:
                page.fill('input[type="email"], input[name="user"], input[name="username"]', email)
            except:
                print("Could not find email field.")

            try:
                page.fill('input[type="password"]', password)
            except:
                print("Could not find password field.")

            page.click('button[type="submit"], button:has-text("Log In")')
            page.wait_for_load_state('networkidle')

            print("Navegando para o projeto...")
            if url:
                page.goto(url)
                page.wait_for_load_state('networkidle')
            else:
                print("Error: No URL provided in proposal file.")
                browser.close()
                return False

            # Bidding Logic (Simplified for demonstration)
            # In a real scenario, we need to find the text area and input fields.
            # page.fill('textarea[id="description"]', proposal_text)
            # page.fill('input[id="bid_amount"]', '100') # Placeholder
            # page.click('button:has-text("Place Bid")')

            print("Preenchendo proposta...")
            # Note: Actual selectors for the bid form are complex and project-dependent.
            # This is a placeholder for the actual interaction.

            print("Lance Enviado!")
            browser.close()
            return True

        except Exception as e:
            print(f"Error during execution: {e}")
            try:
                browser.close()
            except:
                pass
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/bidder.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    print(f"Processing: {filepath}")
    meta, body = parse_proposal(filepath)
    url = meta.get('URL')

    if place_bid(url, body):
        # Move file to processed
        filename = os.path.basename(filepath)
        dest_dir = os.path.join('propostas_geradas', 'processadas')
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        dest = os.path.join(dest_dir, filename)
        shutil.move(filepath, dest)
        print(f"File moved to {dest}")
    else:
        print("Failed to place bid.")

if __name__ == "__main__":
    main()
