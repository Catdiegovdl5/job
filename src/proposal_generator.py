import os
import requests
import json
import random

# Default Config - can be overridden by GUI settings
DEFAULT_MODEL = "gemini-pro"
DEFAULT_TEMP = 0.7

def generate_proposal_ai(job_description, platform, api_key=None, model=DEFAULT_MODEL, temperature=DEFAULT_TEMP, title=None, skills=None):
    """
    Generates a proposal using Google Gemini API based on the job description.
    """
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Error: GEMINI_API_KEY not found. Please configure in settings."

    prompt = f"""
    Aja como um Freelancer Senior Expert em {platform}.
    Escreva uma proposta curta de 3 parágrafos focada em ROI (Retorno sobre Investimento) e na Stack Técnica mencionada na descrição abaixo.

    Projeto: {title}
    Descrição: "{job_description}"
    Skills: {skills}

    A proposta deve ser persuasiva, profissional e direta. Evite clichês como "I am perfect for this".
    Comece com uma análise do problema (Reverse Engineering).
    Termine com um Call to Action (CTA) para call/chat.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 800
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if 'candidates' in data and data['candidates']:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: No response from AI. Details: {json.dumps(data)}"
    except Exception as e:
        return f"Error generating proposal: {str(e)}"

if __name__ == "__main__":
    # Test
    desc = "Need a Python expert to scrape data from Amazon using Playwright."
    print(generate_proposal_ai(desc, "Freelancer.com", title="Amazon Scraper", skills="Python, Web Scraping"))
