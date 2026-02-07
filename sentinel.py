import os
import requests
import json
import logging
from datetime import datetime
from src.config import ARSENAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurações do Jules (Use sua API Key do Google AI Studio)

def call_jules(project_desc, platform):
    """
    Calls the Gemini API to generate a proposal based on the project description and platform.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY is not set.")
        return "Error: GEMINI_API_KEY environment variable not set."

    # Constructing a detailed prompt using the full ARSENAL
    arsenal_text = "\n".join([f"- {k.capitalize()}: {v}" for k, v in ARSENAL.items()])

    prompt = f"""
    Aja como o Jules, Proposals Architect S-Tier.
    Analise este projeto da plataforma {platform}: '{project_desc}'

    Utilize o seguinte arsenal técnico para diferenciar a proposta:
    {arsenal_text}

    Gere uma proposta matadora em {'Português' if platform == '99freelas' else 'Inglês'}.
    Retorne apenas o texto da proposta, focado em resolver os problemas do cliente usando engenharia reversa e soluções de alto nível.
    """

    # Chamada para API do Gemini (Jules)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        logging.info(f"Calling Gemini API for project: {project_desc[:30]}...")
        response = requests.post(url, json=payload, timeout=30) # Added timeout
        response.raise_for_status()
        data = response.json()

        if 'candidates' in data and data['candidates']:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = f"Error: No candidates returned from API. Response: {json.dumps(data)}"
            logging.error(error_msg)
            return error_msg

    except requests.exceptions.Timeout:
        error_msg = "Error calling Gemini API: Request timed out."
        logging.error(error_msg)
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Error calling Gemini API: {str(e)}"
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.exception(error_msg)
        return error_msg

def fetch_leads():
    """
    Simulates fetching leads from RSS feeds or alerts.
    """
    # Exemplo: Simulação de captura (Aqui você conectaria RSS de Upwork/Freelancer)
    leads = [
        {"platform": "freelancer", "desc": "Need a pro for AI Video and SEO"},
        {"platform": "99freelas", "desc": "Gestor de tráfego com CAPI"}
    ]

    results = []
    for lead in leads:
        logging.info(f"Generating proposal for {lead['platform']}...")
        proposal = call_jules(lead['desc'], lead['platform'])
        results.append({
            "timestamp": datetime.now().isoformat(),
            "platform": lead['platform'],
            "description": lead['desc'],
            "proposal": proposal
        })

    output_file = "leads_ready.json"
    try:
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logging.info(f"Results saved to {output_file}")
    except IOError as e:
        logging.error(f"Failed to save results to {output_file}: {e}")

if __name__ == "__main__":
    fetch_leads()
