import os
import sys
import requests
import json
import time
import logging
from datetime import datetime

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from strategies import ProposalStrategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações do Jules (Use sua API Key do Google AI Studio)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def call_jules(project_desc, platform):
    """
    Calls the Gemini API to generate a proposal based on the project description and platform.
    """
    prompt = ProposalStrategy.get_prompt(platform, project_desc)

    # URL without API key
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    # Headers with API key
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if 'candidates' in data and data['candidates']:
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                logger.error(f"No candidates returned. Response: {json.dumps(data)}")
                return f"Error: No candidates returned from API."

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}/{retries} failed: {str(e)}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed to call Gemini API after {retries} attempts.")
                return f"Error calling Gemini API: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Error: {str(e)}"

def fetch_leads():
    """
    Simulates fetching leads from RSS feeds or alerts.
    """
    # Exemplo: Simulação de captura (Aqui você conectaria RSS de Upwork/Freelancer)
    leads = [
        {"platform": "freelancer", "desc": "Need a pro for AI Video and SEO"},
        {"platform": "99freelas", "desc": "Gestor de tráfego com CAPI"},
        {"platform": "upwork", "desc": "Seeking expert for large scale SEO project with Knowledge Graph"}
    ]

    results = []
    for lead in leads:
        logger.info(f"Generating proposal for {lead['platform']}...")
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
        logger.info(f"Results saved to {output_file}")
    except IOError as e:
        logger.error(f"Failed to save results to {output_file}: {e}")

if __name__ == "__main__":
    fetch_leads()
