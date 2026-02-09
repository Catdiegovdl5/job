
import requests
import os
import logging
import time

logger = logging.getLogger("JulesAI")

class JulesAI:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        # Lista de Modelos (Do mais potente ao mais leve)
        self.models = [
            "gemini-2.0-flash",       # Tentativa 1 (Equilibrado)
            "gemini-2.5-flash",       # Tentativa 2 (Potente)
            "gemini-1.5-flash",       # Tentativa 3 (Leve)
            "gemini-pro"              # Tentativa 4 (Clássico)
        ]

    def generate_content(self, prompt):
        if not self.api_key: return None

        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        for model in self.models:
            # Tenta na versão beta (mais recursos)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            
            try:
                # logger.info(f"🧠 Tentando: {model}...") 
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data:
                        return data['candidates'][0]['content']['parts'][0]['text']
                
                elif response.status_code == 429:
                    # AQUI ESTÁ O SEGREDO: Se der 429, espera 10s antes de tentar o próximo
                    logger.warning(f"🚦 Tráfego alto (429) no {model}. Esperando 10s para rotacionar...")
                    time.sleep(10)
                    continue 
                
                elif response.status_code == 404:
                    continue # Só não existe, tenta o próximo rápido
                    
            except Exception as e:
                logger.error(f"Erro conexao {model}: {e}")
                time.sleep(2) # Pequena pausa em caso de erro de rede
        
        return None
