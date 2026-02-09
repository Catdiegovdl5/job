
import os
import time
import logging
from src.proposal_generator import generate_proposal

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("Jules-Sniper")

def get_mock_projects():
    return [
        {"id": "real_101", "title": "Scraper de Preços Amazon", "description": "Preciso de um bot que pegue preços diários de notebooks."},
        {"id": "real_102", "title": "Automação de Lead Gen LinkedIn", "description": "Extrair contatos de CEOs de imobiliárias em SP."},
        {"id": "real_103", "title": "Script Python para Excel", "description": "Automatizar relatórios mensais de 50 planilhas de vendas."}
    ]

def sync_to_github():
    print("🚀 Sincronizando com GitHub...")
    os.system("git add output/*.txt")
    os.system("git commit -m 'Sniper Report: Atualização de Propostas'")
    os.system("git push origin main")

def hunt():
    print("-" * 50)
    print("🦅 JULES SNIPER: INICIANDO VARREDURA...")
    print("-" * 50)
    
    # Se não houver token real, usamos alvos de alto valor simulados
    alvos = get_mock_projects()
    
    if not os.path.exists('output'): os.makedirs('output')

    for alvo in alvos:
        logger.info(f"🎯 ALVO LOCALIZADO: {alvo['title']}")
        
        # O Jules gera a inteligência aqui
        proposta = generate_proposal("freelancer", alvo['description'], use_ai=True)
        
        # Salva o loot
        file_path = f"output/PROPOSTA_{alvo['id']}.txt"
        with open(file_path, "w") as f_out:
            f_out.write(proposta)
        
        logger.info(f"✅ Proposta salva em: {file_path}")
    
    # Protocolo Auto-Push
    sync_to_github()

if __name__ == "__main__":
    while True:
        hunt()
        print("⏳ Aguardando 60s para próxima caçada...")
        time.sleep(60)
