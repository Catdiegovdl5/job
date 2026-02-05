from playwright.sync_api import sync_playwright
import subprocess
import os
import sys
import argparse

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
                    page.wait_for_selector('a.JobSearchCard-primary-heading-link', timeout=5000)
                    job_links = page.locator('a.JobSearchCard-primary-heading-link').all()
                except:
                    # Fallback or different layout
                    print("[WARN] Seletor específico não encontrado, tentando busca genérica de links de projetos...")
                    job_links = page.locator('a[href^="/projects/"]').all()

                print(f"[INFO] Encontrados {len(job_links)} potenciais vagas para '{query}'. Analisando...")

                for link in job_links:
                    try:
                        title = link.inner_text().strip()
                        href = link.get_attribute('href')

                        # Fix relative URLs
                        if href and not href.startswith('http'):
                            href = f"https://www.freelancer.com{href}"

                        # Get full card text for better scoring
                        card = link.locator("xpath=../..")
                        full_card_text = card.inner_text()

                        score, matched_words = calculate_score(full_card_text)
                        keywords_str = ", ".join(matched_words)

                        if score >= MIN_SCORE:
                            print(f"[MATCH] Score {score} ({keywords_str}): {title}")
                            found_links.add(href)
                        else:
                            print(f"[REJEITADO] Score {score} ({keywords_str}): {title}")

                    except Exception as e:
                        # Ignore individual link errors
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

    # 1. Clear old links (optional, but good for a fresh run)
    if os.path.exists(LINKS_FILE):
        os.remove(LINKS_FILE)

    # 2. Scout Jobs
    links = scout_jobs(visual_mode=args.visual)

    # 3. Save Links
    save_links(links)

    # 4. Run Master Template
    run_master_template(visual_mode=args.visual)

if __name__ == "__main__":
    main()
