import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from src.proposal_generator import ARSENAL, PROMPT_TEMPLATES

# Load environment variables
load_dotenv()

# Configurações do Jules (Use sua API Key do Google AI Studio)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def call_jules(project_desc, platform):
    """
    Calls the Gemini API to generate a proposal based on the project description and platform.
    """
    # Identify platform key
    platform_key = platform.lower().strip()
    if "freelancer" in platform_key:
        platform_key = "freelancer"
    elif "99freelas" in platform_key:
        platform_key = "99freelas"
    elif "upwork" in platform_key:
        platform_key = "upwork"
    else:
        # Default fallback if platform is unknown
        platform_key = "freelancer"

    template = PROMPT_TEMPLATES.get(platform_key, "")

    prompt = f"""
    ROLE: You are Jules, an elite software architect and proposal expert.
    TASK: Generate a winning proposal for a project on {platform}.

    PROJECT DESCRIPTION:
    "{project_desc}"

    TECHNICAL ARSENAL (Use these technologies where relevant):
    {json.dumps(ARSENAL, indent=2)}

    INSTRUCTIONS:
    1. Analyze the client's needs using Reverse Engineering.
    2. Write the proposal in the language specified in the template below.
    3. STRICTLY FOLLOW the structure and content of the template below. Fill in the placeholders (like {{video}}, {{traffic}}) with specific context from the Arsenal and the project description.

    TEMPLATE TO FOLLOW:
    '''
    {template}
    '''

    OUTPUT:
    Return ONLY the proposal text.
    """

    # Chamada para API do Gemini (Jules)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        if not GEMINI_API_KEY:
            return "Error: GEMINI_API_KEY not found in environment variables."

        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'candidates' in data and data['candidates']:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: No candidates returned from API. Response: {json.dumps(data)}"
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def fetch_leads():
    """
    Fetches leads from a local file 'leads_input.json' if it exists,
    otherwise uses simulated data.
    """
    input_file = "leads_input.json"
    leads = []

    if os.path.exists(input_file):
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                leads = json.load(f)
            print(f"Loaded {len(leads)} leads from {input_file}")
        except Exception as e:
            print(f"Error reading {input_file}: {e}")

    if not leads:
        print("No input file found or empty. Using simulated data.")
        # Exemplo: Simulação de captura (Aqui você conectaria RSS de Upwork/Freelancer)
        leads = [
            {"platform": "freelancer", "description": "Need a pro for AI Video and SEO"},
            {"platform": "99freelas", "description": "Gestor de tráfego com CAPI"}
        ]

    results = []
    for lead in leads:
        print(f"Generating proposal for {lead['platform']}...")

        # Normalize description key
        description = lead.get('description') or lead.get('desc')

        # Add basic validation
        if not description or not lead.get('platform'):
            print(f"Skipping invalid lead: {lead}")
            continue

        proposal = call_jules(description, lead['platform'])
        results.append({
            "timestamp": datetime.now().isoformat(),
            "platform": lead['platform'],
            "description": lead.get('description') or lead.get('desc'),
            "proposal": proposal
        })

    output_file = "leads_ready.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    fetch_leads()
