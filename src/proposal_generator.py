
def generate_simulation_proposal(description):
    return f"""
--- [MODO SIMULAÇÃO S-TIER ATIVO] ---
ALVO: {description[:50]}...

1. O GANCHO TÉCNICO (The Hook):
Identificamos a necessidade de automação robusta. Usaremos Playwright para evitar detecção.

2. PROVA DE CÓDIGO:
import asyncio
from playwright.async_api import async_playwright
# Lógica Stealth ativada para este alvo.

3. ROADMAP:
Fase 1: Setup & Bypass | Fase 2: Extração | Fase 3: Deploy.

ROI: Redução estimada de 90% no esforço manual.
CTA: "Ambiente pronto para teste. Vamos conversar?"
"""

def generate_proposal(platform, description, questions=None, use_ai=False):
    # Tenta carregar IA, se falhar ou não tiver chave, vai para Simulação
    try:
        from src.ai_client import JulesAI
        from src.config import GEMINI_API_KEY
        
        if use_ai and GEMINI_API_KEY:
            ai = JulesAI()
            # Prompt simplificado para o teste
            prompt = f"Gere uma proposta para: {description}"
            return ai.generate_content(prompt)
    except Exception:
        pass
        
    return generate_simulation_proposal(description)
