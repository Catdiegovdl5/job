
from src.ai_client import JulesAI
import os

def generate_simulation_proposal(description):
    return f"""
--- [MODO MANUAL] ---
ALVO: {description}
ERRO: IA Indisponível.
RECOMENDAÇÃO: Enviar proposta template manual.
"""

def generate_proposal(platform, description, questions=None, use_ai=True):
    # 1. Tenta usar a IA
    if use_ai:
        try:
            brain = JulesAI()
            
            prompt = f"""
            ROLE: Senior Python Developer.
            TASK: Write a short, aggressive freelance proposal.
            PROJECT: {description}
            STRUCTURE:
            - Hook (I understood the problem)
            - Solution (Libraries I will use)
            - CTA (Let's chat)
            """
            
            response = brain.generate_content(prompt)
            
            if response:
                return response
                
        except Exception as e:
            print(f"⚠️ Erro no gerador: {e}")
            
    # 2. Fallback para Simulação se a IA falhar
    return generate_simulation_proposal(description)
