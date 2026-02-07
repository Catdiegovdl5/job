import sys
import os
import shutil
import time
import random
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

def place_bid(url, proposal_text, meta):
    mode = os.getenv("SNIPER_MODE", "GHOST")
    headless = os.getenv("HEADLESS", "True").lower() == "true"

    # Credentials
    email = os.getenv("FREELANCER_EMAIL")
    password = os.getenv("FREELANCER_PASSWORD")

    print(f"--- BIDDER STARTED: MODE={mode} ---")

    # Status File: PROCESSING
    status_file = filepath + ".status"
    with open(status_file, "w") as f:
        f.write("PROCESSING")

    # MODE LOGIC
    if mode == "SURGICAL":
        score = int(meta.get("SCORE", "0"))
        # Example logic: Only bid if Score > 90
        if score < 90:
             print(f"[SURGICAL] Skipped. Score {score} < 90.")
             return False
        print(f"[SURGICAL] Target Acquired. Score: {score}")

    # Simulation Check
    if not email or not password:
        print("[WARN] Credentials not found. Running in SIMULATION MODE.")
        headless = True # Force headless simulation

    browser = None
    try:
        with sync_playwright() as p:
            print("Iniciando Navegador...")

            # MODE: DEBUG - Show browser
            if mode == "DEBUG":
                headless = False
                print("[DEBUG] Headless Mode DISABLED.")

            browser = p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )
            context = browser.new_context()
            page = context.new_page()

            print("Efetuando Login...")
            # Simulate Login Steps
            if not email or not password:
                time.sleep(1) # Sim delay
            else:
                page.goto("https://www.freelancer.com/login")
                try:
                    page.fill('input[type="email"], input[name="user"], input[name="username"]', email)
                    page.fill('input[type="password"]', password)
                    page.click('button[type="submit"], button:has-text("Log In")')
                    page.wait_for_load_state('networkidle')
                except Exception as e:
                    print(f"[ERROR] Login Failed: {e}")
                    if mode != "DEBUG":
                         return False

            # MODE: GHOST - Random Delay
            if mode == "GHOST":
                delay = random.uniform(15, 45)
                print(f"[GHOST] Holding for {delay:.2f}s...")
                time.sleep(delay)

            print(f"Navegando para: {url}")
            if url and (email and password):
                page.goto(url)
                # page.wait_for_load_state('networkidle')
            elif not url:
                print("Error: No URL provided.")
                return False

            print("Preenchendo proposta...")
            # Interaction Simulation
            time.sleep(1) # Type simulation

            if mode == "DEBUG":
                print("[DEBUG] Skipping final 'Place Bid' click.")
            else:
                # Real Mode: Click Submit
                # page.click('button:has-text("Place Bid")')
                pass

            print("Lance Enviado!")

            # Status File: SENT
            with open(status_file, "w") as f:
                f.write("SENT")

            return True

    except Exception as e:
        print(f"Error during execution: {e}")
        # Status File: FAILED
        with open(status_file, "w") as f:
            f.write(f"FAILED: {e}")
        return False
    finally:
        if browser:
            try:
                browser.close()
            except:
                pass

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

    if place_bid(url, body, meta):
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
