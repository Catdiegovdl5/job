import os
import logging
from src.proposal_generator import generate_proposal

# Leads Simulados para Teste
SIMULATED_LEADS = [
    {"platform": "freelancer", "desc": "Looking for SEO expert to rank my Shopify store on Google and fix speed issues"},
    {"platform": "freelancer", "desc": "Need a python script to scrape data from 3 websites and save to excel"},
    {"platform": "freelancer", "desc": "Create an AI video for my marketing campaign"}
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("Sentinel")

def process_leads():
    if not os.path.exists("output"): os.makedirs("output")
    
    # Limpa output antigo
    for f in os.listdir("output"):
        if f.endswith(".txt"): os.remove(os.path.join("output", f))

    for i, lead in enumerate(SIMULATED_LEADS):
        desc = lead.get("desc", "")
        logger.info(f"🎯 Alvo Detectado: {desc[:40]}...")
        
        proposal = generate_proposal("freelancer", desc, use_ai=True)
        
        filename = f"output/PROPOSTA_{i}_freelancer.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"TITLE: {desc}\nURL: https://www.freelancer.com/projects/fake/{i}\n---\n{proposal}")
        
        logger.info(f"✅ Salvo em: {filename}")

if __name__ == "__main__":
    process_leads()
