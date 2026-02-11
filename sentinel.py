import os
import requests
import json
from datetime import datetime

# Configurações do Diego (Use sua API Key do Google AI Studio)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def save_memory(data):
    """
    Saves the leads/proposals data to a JSON file.
    """
    output_file = "leads_ready.json"
    try:
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving memory: {e}")

def gerar_proposta_groq(project_desc, platform):
    """
    Calls the AI API (currently Gemini acting as Diego) to generate a proposal.
    """
    prompt = f"""
SYSTEM OVERRIDE: You are DIEGO, a Python Architect. You represent a premium agency. You are NOT an AI. STOP acting like a generic freelancer.

Write a bid for '{project_desc}'. START DIRECTLY with the technical solution (e.g., 'I will build a Dockerized Python script...'). NO greeting. NO fluff. Sign strictly as: 'Diego'.

Platform: {platform}
Arsenal: Veo 3, Nano Banana, CAPI, GEO, AEO.
    """

    # Chamada para API do Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'candidates' in data and data['candidates']:
            texto_final = data['candidates'][0]['content']['parts'][0]['text']

            # Sanitization Filter (Post-Processing)
            texto_final = texto_final.replace("Jules", "Diego")
            texto_final = texto_final.replace("Dear Client,", "")
            texto_final = texto_final.replace("I'm excited to bid", "I analyzed your requirements")

            return texto_final.strip()
        else:
            return f"Error: No candidates returned from API. Response: {json.dumps(data)}"
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def fetch_leads():
    """
    Simulates fetching leads from RSS feeds or alerts.
    """
    # Exemplo: Simulação de captura
    leads = [
        {"platform": "freelancer", "desc": "Need a pro for AI Video and SEO"},
        {"platform": "99freelas", "desc": "Gestor de tráfego com CAPI"}
    ]

    results = []
    for lead in leads:
        print(f"Generating proposal for {lead['platform']}...")
        proposal = gerar_proposta_groq(lead['desc'], lead['platform'])
        results.append({
            "timestamp": datetime.now().isoformat(),
            "platform": lead['platform'],
            "description": lead['desc'],
            "proposal": proposal
        })

    save_memory(results)

if __name__ == "__main__":
    fetch_leads()
