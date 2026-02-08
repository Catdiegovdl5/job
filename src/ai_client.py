import requests
import json
import time
import os
try:
    from .config import GEMINI_API_KEY
except ImportError:
    from config import GEMINI_API_KEY

class JulesAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or GEMINI_API_KEY
        # Tenta conectar no endpoint mais estável
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def generate_content(self, prompt, retries=3):
        if not self.api_key: return "Erro: API Key faltando no .env"
        
        url = f"{self.base_url}?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    print(f"Erro API ({response.status_code}): {response.text}")
            except Exception as e:
                print(f"Erro conexão: {e}")
            time.sleep(1)
        return "FALHA CRÍTICA NA IA."
