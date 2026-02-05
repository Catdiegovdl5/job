import argparse
import sys
import os
from bs4 import BeautifulSoup
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def scrape_url(page, url):
    """
    Scrapes the content of the given URL using Playwright.
    Attempts to be smart by looking for article/main tags, falling back to body.
    Includes specific logic for Freelancer.com project descriptions.
    """
    print(f"[DEBUG] Iniciando scrape_url para: {url}")

    try:
        page.goto(url, timeout=60000)
        # Try to wait for the primary description selector
        try:
            page.wait_for_selector('.PageProjectView-description', timeout=5000)
        except:
            print("[DEBUG] Primary selector wait timed out, proceeding with checking list...")

        # Clean Title
        title = page.title()
        if title:
            # Remove common suffixes
            title = title.split(" | ")[0].split(" - ")[0]
            print(f"[DEBUG] Título capturado: {title}")
        else:
            title = "seu projeto"

        # Selectors for Freelancer.com and generic fallbacks
        selectors = [
            '.PageProjectView-description',
            '.project-description',
            '#project-description',
            '[class*="ProjectView-description"]',
            'div.project-description',
            'section.JobDescription',
            'article',
            'main'
        ]

        text_content = ""
        found_valid_content = False

        for selector in selectors:
            print(f"[DEBUG] Tentando seletor: {selector}")
            # Use query_selector_all via locator logic
            if page.locator(selector).count() > 0:
                elements = page.locator(selector).all()
                temp_text = ""
                for el in elements:
                    temp_text += el.inner_text() + " "

                temp_text = temp_text.strip()
                print(f"[DEBUG] Texto encontrado (len={len(temp_text)}) com seletor '{selector}'.")

                # Noise Removal: Filter out common menu/navigation phrases
                noise_phrases = ["log in", "sign up", "post a project", "hire freelancers", "find work", "solutions"]
                lines = temp_text.split('\n')
                cleaned_lines = []
                for line in lines:
                    line_lower = line.lower()

                    # Category Line Cleaner: Remove lines that are just category headers
                    # Examples: "Jobs > Digital Marketing", "Digital Marketing", "Web Development"
                    if "jobs >" in line_lower or line_lower.strip() in ["digital marketing", "web development"]:
                        print(f"[DEBUG] Removendo linha de categoria/breadcrumb: '{line.strip()}'")
                        continue

                    if not any(noise in line_lower for noise in noise_phrases):
                        cleaned_lines.append(line)

                temp_text = "\n".join(cleaned_lines).strip()

                # Anti-Boilerplate Validation (Checking for "By skill" leakage specifically)
                bad_phrases = ["by skill", "search for freelancers"]
                found_bad = False
                for phrase in bad_phrases:
                    if phrase in temp_text.lower():
                        found_bad = True
                        if len(temp_text) > 500:
                            # Partial Cleaning Logic
                             print(f"[DEBUG] Tentando limpar boilerplate '{phrase}' de texto longo...")
                             lines = temp_text.split('\n')
                             cleaned_lines = [line for line in lines if phrase not in line.lower()]
                             temp_text = "\n".join(cleaned_lines).strip()
                             if not temp_text: # If empty after clean, reject
                                 print(f"[WARN] Texto vazio após limpeza de boilerplate '{phrase}'.")
                                 found_bad = True # Treat as bad to try next selector
                             else:
                                 print(f"[DEBUG] Texto limpo com sucesso. Novo tamanho: {len(temp_text)}")
                                 found_bad = False # It's acceptable now
                        else:
                            print(f"[WARN] Rejeitado: Boilerplate '{phrase}' detectado em texto curto.")
                        break

                if found_bad:
                    continue # Try next selector

                text_content = temp_text
                if text_content:
                    found_valid_content = True
                    break

        # Absolute fallback to body if no specific selector worked
        if not found_valid_content:
            print("[DEBUG] Tentando seletor de fallback: body (filtrado)")
            temp_text = page.locator("body").inner_text()

            # Noise Removal again for body
            noise_phrases = ["log in", "sign up", "post a project", "hire freelancers", "find work", "solutions"]
            lines = temp_text.split('\n')
            cleaned_lines = []
            for line in lines:
                 if not any(noise in line.lower() for noise in noise_phrases):
                     cleaned_lines.append(line)
            temp_text = "\n".join(cleaned_lines).strip()

            # Basic check again
            if "by skill" not in temp_text.lower() and "search for freelancers" not in temp_text.lower():
                text_content = temp_text
                print(f"[DEBUG] Texto encontrado no body (len={len(text_content)})")

        if not text_content:
             print(f"[WARN] Proposta ignorada. URL: {url} | Motivo: Nenhum conteúdo válido encontrado após tentar todos seletores.")
             return None, None

        return text_content.strip(), title

    except Exception as e:
        print(f"\n[ERROR] Falha ao acessar a URL com Playwright: {e}")
        # Re-raise to show in logs if needed, or return None
        raise e

def determine_core(description):
    """
    Determines the core (Data, Tech, Marketing) based on keywords in the description.
    """
    description_lower = description.lower()

    # Keywords definitions
    data_keywords = ['excel', 'dados', 'financeiro', 'planilha']
    tech_keywords = ['performance', 'android', 'automação', 'python', 'tech', 'mongodb', 'react', 'frontend', 'backend', 'node']
    marketing_keywords = ['ads', 'tráfego', 'vendas', 'marketing', 'facebook', 'meta', 'instagram', 'google ads', 'tiktok', 'anúncios']

    # Priority Implementation: Marketing -> Tech -> Data
    # "Strong Match" for Marketing keywords (Tráfego, Ads, Anúncios) implied by check order and expanded list

    if any(k in description_lower for k in marketing_keywords):
        return 'Marketing'
    elif any(k in description_lower for k in tech_keywords):
        return 'Tech'
    elif any(k in description_lower for k in data_keywords):
        return 'Data'
    else:
        # Fallback to Tech as a default or could be General
        return 'Tech'

def generate_proposal(core, description, title="seu projeto"):
    """
    Generates the proposal content based on the determined core.
    Tone: INTJ (Logical, direct, ROI-focused).
    Structure: Single fluid text block, <150 words.
    """

    proposal_text = ""

    if core == 'Data':
        proposal_text = f"Vi sua vaga para {title} e identifiquei uma necessidade crítica de estruturação e precisão nos dados.\n\n" \
                        f"Em um projeto recente ('PROCX'), implementei um sistema Microsoft que garantiu 100% de precisão na reconciliação de grandes volumes financeiros.\n\n" \
                        f"Minha proposta é implementar uma arquitetura de dados à prova de falhas, automatizando o processamento e eliminando erros manuais para garantir que suas decisões sejam baseadas em fatos, não em suposições.\n\n" \
                        f"Se você valoriza dados precisos e estruturados para escalar, aguardo seu contato."

    elif core == 'Tech':
        proposal_text = f"Vi sua vaga para {title} e identifiquei que o desafio exige código performático e escalável, não apenas uma solução temporária.\n\n" \
                        f"Desenvolvi o 'Turbo Core', uma refatoração de baixo nível (Kernel/Performance) que aumentou a eficiência do sistema em +40%, impactando diretamente a estabilidade e velocidade.\n\n" \
                        f"Vou aplicar as mesmas práticas de engenharia de software para entregar uma solução robusta, focada em automação e eficiência (Python/Stack Tecnológico), garantindo ROI através da tecnologia.\n\n" \
                        f"Vamos elevar o padrão técnico do seu projeto. Estou à disposição."

    elif core == 'Marketing':
        proposal_text = f"Vi sua vaga para {title} e identifiquei que seu objetivo de tráfego e vendas exige uma estratégia agressiva focada em conversão.\n\n" \
                        f"Com o 'Lead Rescue 10s', criei automações que recuperam leads em segundos, maximizando drasticamente as taxas de conversão de campanhas e reduzindo o CAC.\n\n" \
                        f"Minha abordagem integra tráfego pago com automação de vendas para garantir que cada lead gerado tenha o máximo potencial de fechamento, otimizando seu orçamento de mídia.\n\n" \
                        f"Se busca resultados mensuráveis e crescimento de receita, vamos conversar agora."

    return f"--- PROPOSTA GERADA (Núcleo: {core}) ---\n\n{proposal_text}"

def save_proposal(content, filename="ultima_proposta.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n[INFO] Proposta salva com sucesso em '{filename}'.")
    except Exception as e:
        print(f"\n[ERROR] Falha ao salvar o arquivo: {e}")

def sanitize_filename(name):
    """Sanitizes the filename to be safe for file systems."""
    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Truncate if too long
    return name[:50]

def process_batch(filepath):
    """
    Processes a list of URLs from a file using Playwright (reusing browser).
    """
    print(f"[DEBUG] Entrou em process_batch com arquivo: {filepath}")

    if not os.path.exists(filepath):
        print(f"[ERROR] Arquivo não encontrado: {filepath}")
        sys.exit(1)

    output_dir = "propostas_geradas"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[INFO] Pasta '{output_dir}' criada.")

    with open(filepath, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

    print(f"[DEBUG] URLs carregadas: {len(urls)}")

    total_generated = 0
    total_urls = len(urls)

    with sync_playwright() as p:
        # Launch browser once
        # HEADLESS_MODE is False for the 7 link test as requested
        browser = p.chromium.launch(headless=False)

        for i, url in enumerate(urls, 1):
            print(f"[INFO] Processando URL {i} de {total_urls}...")

            context = browser.new_context()
            page = context.new_page()

            try:
                description, title = scrape_url(page, url)

                if description:
                    print(f"[DEBUG] Texto Extraído: {description[:200]}...")

                    core = determine_core(description)
                    proposal = generate_proposal(core, description, title)

                    # Generate filename
                    if title:
                        safe_title = sanitize_filename(title)
                        filename = f"proposta_{safe_title}.txt"
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        filename = f"proposta_{timestamp}.txt"

                    full_path = os.path.join(output_dir, filename)

                    try:
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(proposal)
                        print(f"[INFO] Salvo em: {full_path}")
                        total_generated += 1
                    except Exception as e:
                        print(f"[ERROR] Falha ao salvar proposta: {e}")

            except Exception as e:
                print(f"[CRITICAL ERROR] Falha ao processar URL {url}: {e}")
                import traceback
                traceback.print_exc()
            finally:
                page.close()
                context.close()

            print("-" * 30)

        browser.close()

    print(f"Total de propostas geradas: {total_generated}")

def main():
    parser = argparse.ArgumentParser(description="Proposals Architect S-Tier - Master Template")
    parser.add_argument("--description", help="Descrição da vaga/projeto (Prioridade sobre URL)")
    parser.add_argument("--url", help="URL da vaga para extração automática")
    parser.add_argument("--file", help="Arquivo .txt com lista de URLs para processamento em lote")

    args = parser.parse_args()

    if args.file:
        print(f"[INFO] Iniciando Modo Batch com arquivo: {args.file}")
        process_batch(args.file)
        sys.exit(0)

    description = ""
    title = "seu projeto"

    if args.description:
        description = args.description
        print("[INFO] Usando descrição fornecida manualmente.")
    elif args.url:
        # Also unprotected call here
        try:
            print(f"[INFO] Iniciando Web Scraping da URL (Single Mode with Playwright): {args.url}")
            # Single mode needs its own browser logic
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                try:
                    description, title = scrape_url(page, args.url)
                    print(f"[INFO] Texto extraído com sucesso. Título: {title}")
                finally:
                    browser.close()

        except Exception as e:
            print(f"[CRITICAL ERROR] Falha na execução principal: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    else:
        print("[ERROR] Você deve fornecer --description, --url ou --file.")
        parser.print_help()
        sys.exit(1)

    # Debug Output
    if description:
        print(f"[DEBUG] Texto Extraído: {description[:200]}...")

        # 1. Determine Core
        core = determine_core(description)
        print(f"[INFO] Núcleo Determinado: {core}")

        # 2. Generate Proposal
        proposal = generate_proposal(core, description, title)

        # 3. Output to Screen
        print(proposal)

        # 4. Save to File
        save_proposal(proposal)

if __name__ == "__main__":
    main()
