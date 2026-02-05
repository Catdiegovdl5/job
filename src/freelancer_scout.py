from playwright.sync_api import sync_playwright
import subprocess
import os
import sys

# Configuration
HEADLESS_MODE = False  # User requested False to see the robot in action
LINKS_FILE = "links.txt"
MIN_SCORE = 5

# Weights definition
STRONG_WORDS = ['Turbo Core', 'n8n', 'PROCX', 'Facebook Ads', 'Automation']
GENERAL_WORDS = ['Script', 'Data', 'Marketing', 'Excel']

def calculate_score(text):
    """
    Calculates the score based on the text and defined weights.
    Formula: Score = (Strong_Points * 2) + General_Points
    """
    score = 0
    text_lower = text.lower()

    # Check Strong Words (Weight 2)
    for word in STRONG_WORDS:
        if word.lower() in text_lower:
            score += 2

    # Check General Words (Weight 1)
    for word in GENERAL_WORDS:
        if word.lower() in text_lower:
            score += 1

    return score

def scout_jobs():
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

    print(f"[INFO] Iniciando o Freelancer Scout (Headless: {HEADLESS_MODE})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE)
        context = browser.new_context()
        page = context.new_page()

        for query in queries:
            url = f"https://www.freelancer.com/jobs/?keyword={query}"
            print(f"[INFO] Acessando: {url}")

            try:
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle")

                # Wait for job listings to appear
                # Freelancer.com usually has job cards in .JobSearchCard-item or similar
                # We will target links inside the job list container

                # Depending on the layout (list vs grid), selectors might vary.
                # A common selector for job titles is often an 'a' tag with class 'JobSearchCard-primary-heading-link'
                # or generically looking for links inside the result list.

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

                        # Calculate Score based on Title (and maybe snippet if available easily, but Title is fastest)
                        # To be more precise as requested ("compará-las com minhas palavras-chave"),
                        # checking the title is the first step.
                        # If we wanted to check description, we'd need to enter each page or scrape the snippet.
                        # For speed in this 'scout' phase, let's use the visible text (Title + snippet if visible).

                        # Often the snippet is in a sibling div. Let's stick to Title for the Score in the loop
                        # to avoid heavy navigation, or check parent text.

                        # Let's try to get the full card text for better scoring
                        card = link.locator("xpath=../..") # Go up to parent card container roughly
                        full_card_text = card.inner_text()

                        score = calculate_score(full_card_text)

                        if score >= MIN_SCORE:
                            print(f"[MATCH] Score {score}: {title}")
                            found_links.add(href)
                        # else:
                        #    print(f"[SKIP] Score {score}: {title}")

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

def run_master_template():
    """Calls master_template.py to process the saved links."""
    if not os.path.exists(LINKS_FILE) or os.path.getsize(LINKS_FILE) == 0:
        print("[INFO] Arquivo de links vazio ou inexistente. Pulando geração de propostas.")
        return

    print("\n" + "="*40)
    print("[INFO] Invocando Master Template para gerar propostas...")
    print("="*40 + "\n")

    cmd = [sys.executable, "src/master_template.py", "--file", LINKS_FILE]
    subprocess.run(cmd)

def main():
    # 1. Clear old links (optional, but good for a fresh run)
    if os.path.exists(LINKS_FILE):
        os.remove(LINKS_FILE)

    # 2. Scout Jobs
    links = scout_jobs()

    # 3. Save Links
    save_links(links)

    # 4. Run Master Template
    run_master_template()

if __name__ == "__main__":
    main()
