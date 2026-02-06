import argparse
import sys
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
import subprocess
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv("src/.env")

def send_telegram_notification(message):
    """
    Sends a notification to Telegram using environment variables.
    Requires TELEGRAM_TOKEN and TELEGRAM_CHAT_ID to be set in the environment.
    """
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[WARN] Telegram credentials not found in environment (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID). Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"[ERROR] Failed to send Telegram alert: {response.text}")
        else:
            print("[INFO] Telegram alert sent successfully.")
    except Exception as e:
        print(f"[ERROR] Exception sending Telegram alert: {e}")

def scrape_url(page, url):
    """
    Scrapes the content of the given URL using Playwright.
    Attempts to be smart by looking for article/main tags, falling back to body.
    Includes specific logic for Freelancer.com project descriptions.
    """
    print(f"[DEBUG] Iniciando scrape_url para: {url}")

    try:
        page.goto(url, timeout=60000)
        try:
            page.wait_for_selector('.PageProjectView-description', timeout=5000)
        except:
            print("[DEBUG] Primary selector wait timed out, proceeding with checking list...")

        # Clean Title
        title = page.title()
        if title:
            title = title.split(" | ")[0].split(" - ")[0]
            print(f"[DEBUG] Título capturado: {title}")
        else:
            title = "seu projeto"

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
            if page.locator(selector).count() > 0:
                elements = page.locator(selector).all()
                temp_text = ""
                for el in elements:
                    temp_text += el.inner_text() + " "

                temp_text = temp_text.strip()
                print(f"[DEBUG] Texto encontrado (len={len(temp_text)}) com seletor '{selector}'.")

                # Noise Removal
                noise_phrases = ["log in", "sign up", "post a project", "hire freelancers", "find work", "solutions"]
                lines = temp_text.split('\n')
                cleaned_lines = []
                for line in lines:
                    line_lower = line.lower()
                    if "jobs >" in line_lower or line_lower.strip() in ["digital marketing", "web development"]:
                        print(f"[DEBUG] Removendo linha de categoria/breadcrumb: '{line.strip()}'")
                        continue
                    if not any(noise in line_lower for noise in noise_phrases):
                        cleaned_lines.append(line)

                temp_text = "\n".join(cleaned_lines).strip()

                # Anti-Boilerplate
                bad_phrases = ["by skill", "search for freelancers"]
                found_bad = False
                for phrase in bad_phrases:
                    if phrase in temp_text.lower():
                        found_bad = True
                        if len(temp_text) > 500:
                             print(f"[DEBUG] Tentando limpar boilerplate '{phrase}' de texto longo...")
                             lines = temp_text.split('\n')
                             cleaned_lines = [line for line in lines if phrase not in line.lower()]
                             temp_text = "\n".join(cleaned_lines).strip()
                             if not temp_text:
                                 print(f"[WARN] Texto vazio após limpeza de boilerplate '{phrase}'.")
                                 found_bad = True
                             else:
                                 print(f"[DEBUG] Texto limpo com sucesso. Novo tamanho: {len(temp_text)}")
                                 found_bad = False
                        else:
                            print(f"[WARN] Rejeitado: Boilerplate '{phrase}' detectado em texto curto.")
                        break

                if found_bad:
                    continue

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
        raise e

def determine_core(description, title=""):
    """
    Determines the core (Data, Tech, Marketing) based on weighted keywords in description and title.
    Formula: Score = (Body_Count * Weight) + (Title_Count * Weight * 3)
    Weights: Strong=2, General=1.
    Returns: (winner_core, max_score)
    """
    description_lower = description.lower()
    title_lower = title.lower() if title else ""

    # Keyword Dictionaries with Weights (Strong=2, General=1)
    cores = {
        'Data': {
            'strong': ['procx', 'power bi', 'sql', 'vba', 'data'],
            'general': ['excel', 'dados', 'financeiro', 'planilha']
        },
        'Tech': {
            'strong': ['mongodb', 'react', 'node', 'turbo core', 'kernel', 'api', 'frontend', 'backend', 'ai', 'bot', 'html', 'dev'],
            'general': ['python', 'tech', 'android', 'automação', 'performance']
        },
        'Marketing': {
            'strong': ['lead rescue', 'tráfego', 'facebook ads', 'google ads', 'meta'],
            'general': ['marketing', 'vendas', 'ads', 'anúncios', 'instagram', 'tiktok']
        }
    }

    scores = {'Data': 0, 'Tech': 0, 'Marketing': 0}

    for core, keywords in cores.items():
        # Calculate Body Score
        for word in keywords['strong']:
            count = description_lower.count(word.lower())
            scores[core] += count * 2
        for word in keywords['general']:
            count = description_lower.count(word.lower())
            scores[core] += count * 1

        # Calculate Title Score (3x Multiplier)
        for word in keywords['strong']:
            count = title_lower.count(word.lower())
            scores[core] += count * 2 * 3
        for word in keywords['general']:
            count = title_lower.count(word.lower())
            scores[core] += count * 1 * 3

    # Log Scoreboard
    print(f"[DEBUG] Scores Finais: Data={scores['Data']}, Tech={scores['Tech']}, Marketing={scores['Marketing']}")

    max_score = max(scores.values())

    # Determine Winner
    # Tie-Breaker: Marketing > Tech > Data
    if scores['Marketing'] >= scores['Tech'] and scores['Marketing'] >= scores['Data'] and scores['Marketing'] > 0:
        winner = 'Marketing'
    elif scores['Tech'] >= scores['Data'] and scores['Tech'] > 0:
        winner = 'Tech'
    elif scores['Data'] > 0:
        winner = 'Data'
    else:
        # Default Fallback if all 0 (or Tech preference)
        winner = 'Tech'

    print(f"[DEBUG] Vencedor: {winner} (Score: {max_score})")
    return winner, max_score

def generate_proposal(core, description, title="seu projeto", score=0, url=""):
    """
    Generates the proposal content based on the determined core.
    Tone: INTJ (Logical, direct, ROI-focused).
    Structure: Single fluid text block, <150 words.
    Includes score and URL in header.
    """

    proposal_text = ""

    if core == 'Data':
        proposal_text = f"Seu projeto de {title} exige precisão cirúrgica e uma arquitetura de dados indestrutível para evitar erros de processamento.\n\n" \
                        f"Como especialista certificado, desenvolvi a metodologia 'PROCX', que automatiza fluxos complexos em SQL/VBA, eliminando 100% das falhas manuais.\n\n" \
                        f"Vou estruturar a sua análise de dados para gerar insights executivos automáticos, garantindo que a informação seja uma ferramenta de decisão, não um peso."

    elif core == 'Tech':
        proposal_text = f"Vi sua vaga para {title} e identifiquei que o desafio exige código performático e escalável, não apenas uma solução temporária.\n\n" \
                        f"Desenvolvi o 'Turbo Core', uma refatoração de baixo nível (Kernel/Performance) que aumentou a eficiência do sistema em +40%.\n\n" \
                        f"Vou aplicar as mesmas práticas de engenharia de software para entregar uma solução robusta (Python/IA), focada em automação e eficiência."

    elif core == 'Marketing':
        proposal_text = f"Vi sua vaga para {title} e identifiquei que seu objetivo de tráfego e vendas exige uma estratégia agressiva focada em conversão.\n\n" \
                        f"Com o 'Lead Rescue 10s', criei automações que recuperam leads em segundos, maximizando drasticamente as taxas de conversão de campanhas e reduzindo o CAC.\n\n" \
                        f"Minha abordagem integra tráfego pago com automação de vendas para garantir que cada lead gerado tenha o máximo potencial de fechamento, otimizando seu orçamento de mídia.\n\n" \
                        f"Se busca resultados mensuráveis e crescimento de receita, vamos conversar agora."

    # Sniper Footer
    footer = "Note: I am a Top-Rated specialist with focus on high-performance ROI and scalable architecture."

    # Header with Score
    header = f"--- PROPOSTA GERADA (Núcleo: {core} | Score: {score}) ---\nURL: {url}"

    return f"{header}\n\n{proposal_text}\n\n{footer}"

def save_proposal(content, filename="ultima_proposta.txt", status="WAITING_APPROVAL"):
    try:
        # Construct filename with status prefix
        final_filename = f"{status}_{filename}" if status else filename
        with open(final_filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n[INFO] Proposta salva com sucesso em '{final_filename}'.")
        return final_filename
    except Exception as e:
        print(f"\n[ERROR] Falha ao salvar o arquivo: {e}")
        return None

def sanitize_filename(name):
    """Sanitizes the filename to be safe for file systems."""
    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Truncate if too long
    return name[:50]

def process_batch(filepath, visual_mode=False, autopilot=False):
    """
    Processes a list of URLs from a file using Playwright (reusing browser).
    """
    print(f"[DEBUG] Entrou em process_batch com arquivo: {filepath}, AutoPilot: {autopilot}")

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

    headless_setting = not visual_mode
    print(f"[INFO] Iniciando navegador (Headless: {headless_setting})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless_setting)

        for i, url in enumerate(urls, 1):
            print(f"[INFO] Processando URL {i} de {total_urls}...")
            context = browser.new_context()
            page = context.new_page()

            try:
                description, title = scrape_url(page, url)

                if description:
                    print(f"[DEBUG] Texto Extraído: {description[:200]}...")

                    core, max_score = determine_core(description, title)
                    proposal = generate_proposal(core, description, title, max_score, url)

                    if title:
                        safe_title = sanitize_filename(title)
                        base_filename = f"{safe_title}.txt"
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        base_filename = f"{timestamp}.txt"

                    full_path = os.path.join(output_dir, base_filename)

                    # AUTOPILOT LOGIC
                    if autopilot and max_score > 85:
                        print(f"[AUTO-PILOT] Score {max_score} > 85. Iniciando lance automático...")
                        saved_path = save_proposal(proposal, full_path, status="SUBMITTED")

                        # Trigger Bidder
                        # We need to pass just the proposal body text
                        proposal_body = proposal.split("\n\n", 1)[1] # Strip Header
                        # Better: Extract body clean here.
                        proposal_clean_body = generate_proposal(core, description, title, max_score, url).split("\n\n", 1)[1]

                        cmd = [sys.executable, "src/bidder.py", url, proposal_clean_body]
                        subprocess.Popen(cmd) # Async call

                        print("[AUTO-PILOT] Bid enviado automaticamente!")
                    else:
                        # Normal Flow -> Waiting for Approval
                        save_proposal(proposal, full_path, status="WAITING_APPROVAL")

                        # Alert if High Score (but not auto-pilot or score <= 85)
                        if max_score > 70:
                            print(f"[SNIPER ALERT] High Value Opportunity Detected! Score: {max_score}")
                            msg = f"🎯 *Sniper Alert*\nJob: {title}\nCore: {core}\nScore: {max_score}\nURL: {url}"
                            send_telegram_notification(msg)

                    total_generated += 1

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
    parser.add_argument("--visual", action="store_true", help="Ativa o modo visível (Headless=False)")
    parser.add_argument("--autopilot", action="store_true", help="Ativa modo Auto-Pilot (Bid direto se Score > 85)")

    args = parser.parse_args()

    if args.file:
        print(f"[INFO] Iniciando Modo Batch com arquivo: {args.file}")
        process_batch(args.file, visual_mode=args.visual, autopilot=args.autopilot)
        sys.exit(0)

    description = ""
    title = "seu projeto"

    if args.description:
        description = args.description
        print("[INFO] Usando descrição fornecida manualmente.")
    elif args.url:
        try:
            print(f"[INFO] Iniciando Web Scraping da URL (Single Mode with Playwright): {args.url}")
            headless_setting = not args.visual
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless_setting)
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

    if description:
        print(f"[DEBUG] Texto Extraído: {description[:200]}...")
        core, max_score = determine_core(description, title)
        print(f"[INFO] Núcleo Determinado: {core} (Score: {max_score})")
        proposal = generate_proposal(core, description, title, max_score, args.url if args.url else "")
        print(proposal)
        # Single mode doesn't really use autopilot logic as it's usually manual check
        save_proposal(proposal, "ultima_proposta.txt", status=None)

if __name__ == "__main__":
    main()
