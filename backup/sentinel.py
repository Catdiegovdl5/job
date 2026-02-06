import os
import requests
import json
from datetime import datetime

# Configurações do Jules (Use sua API Key do Google AI Studio)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def call_jules(project_desc, platform):
    """
    Calls the Gemini API to generate a proposal based on the project description and platform.
    """
    prompt = f"""
    Aja como o Jules, Proposals Architect S-Tier.
    Analise este projeto da plataforma {platform}: '{project_desc}'
    Use o arsenal: Veo 3, Nano Banana, CAPI, GEO, AEO.
    Gere uma proposta matadora em {'Português' if platform == '99freelas' else 'Inglês'}.
    Retorne apenas o texto da proposta.
    """
    # Chamada para API do Gemini (Jules)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
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
    Simulates fetching leads from RSS feeds or alerts.
    """
    # Exemplo: Simulação de captura (Aqui você conectaria RSS de Upwork/Freelancer)
    leads = [
        {"platform": "freelancer", "desc": "Need a pro for AI Video and SEO"},
        {"platform": "99freelas", "desc": "Gestor de tráfego com CAPI"}
    ]

    results = []
    for lead in leads:
        print(f"Generating proposal for {lead['platform']}...")
        proposal = call_jules(lead['desc'], lead['platform'])
        results.append({
            "timestamp": datetime.now().isoformat(),
            "platform": lead['platform'],
            "description": lead['desc'],
            "proposal": proposal
        })

    output_file = "leads_ready.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    fetch_leads()
