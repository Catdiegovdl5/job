
import requests
import os
import logging
import time

logger = logging.getLogger("JulesAI")

class JulesAI:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        # Invertendo a ordem: 1.5-flash é o que mais aceita requisições sem dar 429
        self.models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]

    def generate_content(self, prompt):
        if not self.api_key: return None
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        for model in self.models:
            # Usando a rota v1 estável para maior consistência
            url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={self.api_key}"
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    return response.json()['candidates'][0]['content']['parts'][0]['text']
                
                elif response.status_code == 429:
                    # Aumentamos a espera para 20 segundos para limpar o limite do Google
                    logger.warning(f"🚦 Limite atingido em {model}. Aguardando 20s para resfriar...")
                    time.sleep(20)
                    continue 
                
            except Exception as e:
                time.sleep(5)
                continue
        
        return None
