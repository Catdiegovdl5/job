from playwright.sync_api import sync_playwright
import subprocess
import os
import sys
import argparse
import re
import time

# Configuration
LINKS_FILE = "links.txt"
MIN_SCORE = 3

# Weights definition
STRONG_WORDS = ['Turbo Core', 'n8n', 'PROCX', 'Facebook Ads', 'Automation', 'API', 'Dashboard', 'Scraping', 'Azure', 'CRM']
GENERAL_WORDS = ['Script', 'Data', 'Marketing', 'Excel', 'Finance', 'Sheet', 'Database', 'Optimization', 'Ads', 'Campaign']

def calculate_score(text):
    """
    Calculates the score based on the text and defined weights.
    Formula: Score = (Strong_Points * 2) + General_Points
    Returns: (score, list_of_matched_words)
    """
    score = 0
    matched_words = []
    text_lower = text.lower()

    # Check Strong Words (Weight 2)
    for word in STRONG_WORDS:
        if word.lower() in text_lower:
            score += 2
            matched_words.append(f"{word}(2)")

    # Check General Words (Weight 1)
    for word in GENERAL_WORDS:
        if word.lower() in text_lower:
            score += 1
            matched_words.append(f"{word}(1)")

    return score, matched_words

def check_payment_verified(card_element):
    """Checks if the job card has the 'Payment Verified' badge."""
    try:
        text = card_element.inner_text()
        if "Payment verified" in text or "VERIFIED" in text.upper():
            return True
        return False
    except:
        return False

def check_rating(card_element):
    """Checks if the client rating is >= 4.5. If no rating, returns True (new client)."""
    try:
        text = card_element.inner_text()
        rating_match = re.search(r"(\d\.\d)", text)
        if rating_match:
            rating = float(rating_match.group(1))
            if rating < 4.5:
                return False
        return True # No rating found or rating is high enough
    except:
        return True

def parse_budget_values(text):
    """Parses budget values from text, handling commas and ranges."""
    # Regex matches digits with commas (e.g., 1,500) that follow a $
    matches = re.findall(r"\$([\d,]+)", text)
    if not matches:
        return []

    values = []
    for m in matches:
        try:
            # Remove comma and convert to int
            val = int(m.replace(",", ""))
            values.append(val)
        except:
            continue
    return values

def check_budget(card_element):
    """Checks if budget meets criteria: Hourly >= $30, Fixed >= $200."""
    try:
        text = card_element.inner_text()

        # Check Hourly
        if "/ hr" in text or "Hourly" in text:
            rates = parse_budget_values(text)
            if rates:
                # Sniper Rule: Hourly >= $30/hr
                # If range $10-$30, max is 30.
                max_rate = max(rates)
                if max_rate < 30:
                    return False
        else:
            # Fixed Price
            amounts = parse_budget_values(text)
            if amounts:
                # Sniper Rule: Fixed Budget >= $200
                max_amount = max(amounts)
                if max_amount < 200:
                    return False
        return True
    except:
        return True # Default to keep if parsing fails

def scout_jobs(visual_mode=False):
    """
    Scouts jobs on Freelancer.com using Playwright.
    """
    # Queries to target specific filtered pages
    queries = [
        "python",
        "excel",
        "marketing automation"
    ]

    found_links = set()
    headless_setting = not visual_mode

    print(f"[INFO] Iniciando o Freelancer Scout (Headless: {headless_setting})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless_setting)
        context = browser.new_context()
        page = context.new_page()

        for query in queries:
            url = f"https://www.freelancer.com/jobs/?keyword={query}"
            print(f"[INFO] Acessando: {url}")

            try:
                page.goto(url, timeout=60000)
                try:
                    page.wait_for_load_state("networkidle", timeout=60000)
                except Exception as e:
                    print(f"[WARN] Timeout aguardando networkidle. Prosseguindo... ({e})")

                # Attempt to find job cards
                try:
                    page.wait_for_selector('div.JobSearchCard-item', timeout=5000)
                    job_cards = page.locator('div.JobSearchCard-item').all()
                except:
                    # Fallback or different layout
                    print("[WARN] Seletor específico não encontrado, tentando busca genérica de links de projetos...")
                    job_cards = page.locator('div.JobSearchCard-item-inner').all()

                print(f"[INFO] Encontrados {len(job_cards)} potenciais vagas para '{query}'. Analisando...")

                for card in job_cards:
                    try:
                        # Extract Link and Title first
                        link_el = card.locator('a.JobSearchCard-primary-heading-link').first
                        if link_el.count() == 0:
                            continue

                        title = link_el.inner_text().strip()
                        href = link_el.get_attribute('href')

                        # Fix relative URLs
                        if href and not href.startswith('http'):
                            href = f"https://www.freelancer.com{href}"

                        # Apply Sniper Filters
                        if not check_payment_verified(card):
                            print(f"[REJEITADO] Payment Not Verified: {title}")
                            continue

                        if not check_rating(card):
                            print(f"[REJEITADO] Low Rating: {title}")
                            continue

                        if not check_budget(card):
                            print(f"[REJEITADO] Low Budget: {title}")
                            continue

                        # Calculate Score
                        full_card_text = card.inner_text()
                        score, matched_words = calculate_score(full_card_text)
                        keywords_str = ", ".join(matched_words)

                        if score >= MIN_SCORE:
                            print(f"[MATCH] Score {score} ({keywords_str}): {title}")
                            found_links.add(href)
                        else:
                            print(f"[REJEITADO] Score {score} ({keywords_str}): {title}")

                    except Exception as e:
                        continue

            except Exception as e:
                print(f"[ERROR] Falha ao processar query '{query}': {e}")

        browser.close()

    return list(found_links)

def save_links(links):
    """Saves valid links to the file."""
    if not links:
        print("[INFO] Nenhum link qualificado encontrado desta vez.")
        return

    print(f"[INFO] Salvando {len(links)} links qualificados em {LINKS_FILE}...")
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        for link in links:
            f.write(f"{link}\n")

def run_master_template(visual_mode=False):
    """Calls master_template.py to process the saved links."""
    if not os.path.exists(LINKS_FILE) or os.path.getsize(LINKS_FILE) == 0:
        print("[INFO] Arquivo de links vazio ou inexistente. Pulando geração de propostas.")
        return

    print("\n" + "="*40)
    print("[INFO] Invocando Master Template para gerar propostas...")
    print("="*40 + "\n")

    cmd = [sys.executable, "src/master_template.py", "--file", LINKS_FILE]
    if visual_mode:
        cmd.append("--visual")

    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="Freelancer Scout - Automated Job Hunter")
    parser.add_argument("--visual", action="store_true", help="Ativa o modo visível (Headless=False)")
    args = parser.parse_args()

    # Infinite Loop for Continuous Scouting
    while True:
        print("\n" + "="*50)
        print(f"[SNIPER LOOP] Iniciando nova rodada de caça: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50 + "\n")

        # 1. Clear old links (optional, but good for a fresh run)
        if os.path.exists(LINKS_FILE):
            os.remove(LINKS_FILE)

        # 2. Scout Jobs
        links = scout_jobs(visual_mode=args.visual)

        # 3. Save Links
        save_links(links)

        # 4. Run Master Template
        run_master_template(visual_mode=args.visual)

        # Sleep for 5 minutes
        print("\n[INFO] Ciclo concluído. Entrando em modo de espera por 5 minutos...")
        time.sleep(300)

if __name__ == "__main__":
    main()
