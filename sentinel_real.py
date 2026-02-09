
import time
import logging
import subprocess
import os
from src.proposal_generator import generate_proposal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("SentinelReal")

SIMULATED_LEADS = [
    {
        "platform": "freelancer", 
        "desc": "Preciso de um site WordPress para meu escritório de advocacia. O design deve ser sério, rápido e ter um formulário de contato que envia para meu WhatsApp."
    },
    {
        "platform": "freelancer", 
        "desc": "I need a Telegram Bot that automatically forwards messages from a private channel to a public group. It must handle images and videos, not just text."
    },
    {
        "platform": "freelancer", 
        "desc": "Tenho uma planilha de Excel com 50.000 linhas de vendas bagunçadas. Preciso limpar duplicatas, padronizar nomes e criar um gráfico de vendas por mês."
    }
]

def sync_to_github():
    logger.info("🚀 Enviando relatórios para o QG (GitHub)...")
    try:
        subprocess.run("git add output/*.txt", shell=True)
        subprocess.run("git commit -m 'Sniper Report: Teste com Delay Tático (Anti-429)'", shell=True)
        subprocess.run("git push origin main", shell=True)
        logger.info("✅ Sincronização concluída!")
    except Exception as e:
        logger.warning(f"⚠️ Git Sync: {e}")

def process_radar():
    if not os.path.exists("output"):
        os.makedirs("output")

    logger.info("🦅 JULES SNIPER: INICIANDO BATERIA COM RESFRIAMENTO...")
    
    for i, lead in enumerate(SIMULATED_LEADS):
        desc = lead.get("desc", "")
        logger.info(f"--------------------------------------------------")
        logger.info(f"🎯 ALVO {i+1}: {desc[:40]}...")
        
        # O Jules vai pensar e escrever agora...
        proposal = generate_proposal("freelancer", desc, use_ai=True)
        
        names = ["WP_Advogado_PT", "Telegram_Bot_EN", "Excel_Pandas_PT"]
        filename = f"output/PROPOSTA_TESTE_{names[i]}.txt"
        
        with open(filename, "w", encoding="utf-8") as f_out:
            f_out.write("PROJETO ORIGINAL: " + desc + "\n\n")
            f_out.write("-" * 20 + "\n\n")
            f_out.write(proposal)
        
        logger.info(f"✅ Proposta gerada em: {filename}")
        
        # --- O SEGREDO DO SUCESSO: PAUSA DE 15 SEGUNDOS ---
        if i < len(SIMULATED_LEADS) - 1:
            logger.info("⏳ Resfriando canhões (Aguardando 15s para evitar bloqueio)...")
            time.sleep(15)
    
    sync_to_github()

if __name__ == "__main__":
    process_radar()
