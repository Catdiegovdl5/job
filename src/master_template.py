import argparse
import sys
import os
import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    """
    Scrapes the content of the given URL.
    Attempts to be smart by looking for article/main tags, falling back to body.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Smart scraping logic
        content_tags = soup.find_all(['article', 'main'])

        text_content = ""

        if content_tags:
            for tag in content_tags:
                # Extract text from p tags within the main content areas
                paragraphs = tag.find_all('p')
                if paragraphs:
                    text_content += " ".join([p.get_text(strip=True) for p in paragraphs])
                else:
                    text_content += tag.get_text(strip=True) + " "
        else:
            # Fallback to body but try to avoid nav/footer if possible
            # A simple approach is just grabbing all p tags from body
            paragraphs = soup.body.find_all('p')
            if paragraphs:
                text_content = " ".join([p.get_text(strip=True) for p in paragraphs])
            else:
                # Absolute fallback
                text_content = soup.body.get_text(strip=True)

        return text_content.strip()

    except Exception as e:
        print(f"\n[ERROR] Falha ao acessar a URL: {e}")
        print("Por favor, rode o comando novamente usando a flag --description e cole o texto manualmente.")
        sys.exit(1)

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

def generate_proposal(core, description):
    """
    Generates the proposal content based on the determined core.
    Tone: INTJ (Logical, direct, ROI-focused).
    """

    # Common structure placeholders
    hook = ""
    authority = ""
    solution = ""
    cta = ""

    if core == 'Data':
        hook = "Analisei a descrição do seu projeto e identifiquei uma necessidade crítica de estruturação e precisão nos dados."
        authority = "Em um projeto recente ('Fluxo de Caixa Inteligente'), implementei um sistema que garantiu 100% de precisão na reconciliação de grandes volumes financeiros."
        solution = "Minha proposta é implementar uma arquitetura de dados à prova de falhas, automatizando o processamento e eliminando erros manuais para garantir que suas decisões sejam baseadas em fatos, não em suposições."
        cta = "Se você valoriza dados precisos e estruturados para escalar, aguardo seu contato."

    elif core == 'Tech':
        hook = "Sua descrição aponta para um desafio que exige código performático e escalável, não apenas uma solução temporária."
        authority = "Desenvolvi o 'Turbo Core', uma refatoração crítica que aumentou a performance do sistema em +40%, impactando diretamente a experiência do usuário final."
        solution = "Vou aplicar as mesmas práticas de engenharia de software para entregar uma solução robusta, focada em automação e eficiência (Python/Stack Tecnológico), garantindo ROI através da tecnologia."
        cta = "Vamos elevar o padrão técnico do seu projeto. Estou à disposição."

    elif core == 'Marketing':
        hook = "Seu objetivo de tráfego e vendas exige uma estratégia agressiva focada em conversão, não apenas em métricas de vaidade."
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

def main():
    parser = argparse.ArgumentParser(description="Proposals Architect S-Tier - Master Template")
    parser.add_argument("--description", help="Descrição da vaga/projeto (Prioridade sobre URL)")
    parser.add_argument("--url", help="URL da vaga para extração automática")

    args = parser.parse_args()

    description = ""

    if args.description:
        description = args.description
        print("[INFO] Usando descrição fornecida manualmente.")
    elif args.url:
        print(f"[INFO] Iniciando Web Scraping da URL: {args.url}")
        description = scrape_url(args.url)
        print("[INFO] Texto extraído com sucesso.")
    else:
        print("[ERROR] Você deve fornecer --description ou --url.")
        parser.print_help()
        sys.exit(1)

    # Debug Output
    print(f"[DEBUG] Texto Extraído: {description[:200]}...")

    # 1. Determine Core
    core = determine_core(description)
    print(f"[INFO] Núcleo Determinado: {core}")

    # 2. Generate Proposal
    proposal = generate_proposal(core, description)

    # 3. Output to Screen
    print(proposal)

    # 4. Save to File
    save_proposal(proposal)

if __name__ == "__main__":
    main()
