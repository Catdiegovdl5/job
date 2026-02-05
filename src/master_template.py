import argparse
import sys
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def scrape_url(url, batch_mode=False):
    """
    Scrapes the content of the given URL.
    Attempts to be smart by looking for article/main tags, falling back to body.
    Includes specific logic for Freelancer.com project descriptions.
    """
    print(f"[DEBUG] Iniciando scrape_url para: {url}")
    # Removed broad try-except to allow debugging traceback
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Clean Title
    title = "seu projeto"
    if soup.title:
        raw_title = soup.title.get_text(strip=True)
        # Remove common suffixes
        title = raw_title.split(" | ")[0].split(" - ")[0]
        print(f"[DEBUG] Título capturado: {title}")

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
        content_tags = soup.select(selector)

        if content_tags:
            temp_text = ""
            for tag in content_tags:
                paragraphs = tag.find_all('p')
                if paragraphs:
                    temp_text += " ".join([p.get_text(strip=True) for p in paragraphs])
                else:
                    temp_text += tag.get_text(strip=True) + " "

            temp_text = temp_text.strip()
            print(f"[DEBUG] Texto encontrado (len={len(temp_text)}) com seletor '{selector}'.")

            # Anti-Boilerplate Validation
            bad_phrases = ["by skill", "search for freelancers"]
            found_bad = False
            for phrase in bad_phrases:
                if phrase in temp_text.lower():
                    found_bad = True
                    if len(temp_text) > 500:
                        # Partial Cleaning Logic
                         print(f"[DEBUG] Tentando limpar boilerplate '{phrase}' de texto longo...")
                         # Simple cleaning: remove lines containing the phrase
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
        paragraphs = soup.body.find_all('p')
        if paragraphs:
            temp_text = " ".join([p.get_text(strip=True) for p in paragraphs])
            # Basic check again
            if "by skill" not in temp_text.lower() and "search for freelancers" not in temp_text.lower():
                text_content = temp_text
                print(f"[DEBUG] Texto encontrado no body (len={len(text_content)})")

        if not text_content:
            # Last resort
            temp_text = soup.body.get_text(strip=True)
            # Very basic check
            if "by skill" not in temp_text.lower() and "search for freelancers" not in temp_text.lower():
                 text_content = temp_text
                 print(f"[DEBUG] Texto bruto do body usado (len={len(text_content)})")

    if not text_content:
         print(f"[WARN] Proposta ignorada. URL: {url} | Motivo: Nenhum conteúdo válido encontrado após tentar todos seletores.")
         if batch_mode:
             return None, None

    return text_content.strip(), title


def determine_core(description):
    """
    Determines the core (Data, Tech, Marketing) based on keywords in the description.
    """
    description_lower = description.lower()

    # Keywords definitions
    data_keywords = ['excel', 'dados', 'financeiro', 'planilha']
    tech_keywords = ['performance', 'android', 'automação', 'python', 'tech']
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
    Uses dynamic title in the hook.
    """

    # Common structure placeholders
    hook = ""
    authority = ""
    solution = ""
    cta = ""

    if core == 'Data':
        hook = f"Vi sua vaga para {title} e identifiquei uma necessidade crítica de estruturação e precisão nos dados."
        authority = "Em um projeto recente ('Fluxo de Caixa Inteligente'), implementei um sistema que garantiu 100% de precisão na reconciliação de grandes volumes financeiros."
        solution = "Minha proposta é implementar uma arquitetura de dados à prova de falhas, automatizando o processamento e eliminando erros manuais para garantir que suas decisões sejam baseadas em fatos, não em suposições."
        cta = "Se você valoriza dados precisos e estruturados para escalar, aguardo seu contato."

    elif core == 'Tech':
        hook = f"Vi sua vaga para {title} e identifiquei que o desafio exige código performático e escalável, não apenas uma solução temporária."
        authority = "Desenvolvi o 'Turbo Core', uma refatoração crítica que aumentou a performance do sistema em +40%, impactando diretamente a experiência do usuário final."
        solution = "Vou aplicar as mesmas práticas de engenharia de software para entregar uma solução robusta, focada em automação e eficiência (Python/Stack Tecnológico), garantindo ROI através da tecnologia."
        cta = "Vamos elevar o padrão técnico do seu projeto. Estou à disposição."

    elif core == 'Marketing':
        hook = f"Vi sua vaga para {title} e identifiquei que seu objetivo de tráfego e vendas exige uma estratégia agressiva focada em conversão."
        authority = "Com o 'Lead Rescue 10s', criei automações que recuperam leads em segundos, maximizando drasticamente as taxas de conversão de campanhas."
        solution = "Minha abordagem integra tráfego pago com automação de vendas para garantir que cada lead gerado tenha o máximo potencial de fechamento, otimizando seu orçamento de mídia."
        cta = "Se busca resultados mensuráveis e crescimento de receita, vamos conversar agora."

    # Constructing the full proposal
    # Structure: 1. Gancho Inicial, 2. Prova de Autoridade, 3. Solução Proposta, 4. CTA
    proposal_text = f"""--- PROPOSTA GERADA (Núcleo: {core}) ---

1. Gancho Inicial
{hook}

2. Prova de Autoridade
{authority}

3. Solução Proposta
{solution}

4. Chamada para Ação (CTA)
{cta}
"""
    return proposal_text

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
    Processes a list of URLs from a file.
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

    for i, url in enumerate(urls, 1):
        print(f"[INFO] Processando URL {i} de {total_urls}...")

        try:
             # Call scrape_url directly, let it crash if needed (removed broad try-except inside scrape_url)
             # But here in loop, we might want to catch to continue batch?
             # User said: "remove os try/except silenciosos". So I will catch specific ones or let it crash to see trace.
             # To be safe for batch but verbose:
            description, title = scrape_url(url, batch_mode=True)

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
            # Catching here to show the trace but continue the batch IF desired,
            # or just print error loudly.
            print(f"[CRITICAL ERROR] Falha ao processar URL {url}: {e}")
            import traceback
            traceback.print_exc()

        print("-" * 30)

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
            print(f"[INFO] Iniciando Web Scraping da URL: {args.url}")
            description, title = scrape_url(args.url)
            print(f"[INFO] Texto extraído com sucesso. Título: {title}")
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
