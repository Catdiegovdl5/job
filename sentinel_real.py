import os
import time
import logging
import subprocess
from src.proposal_generator import generate_proposal

# Configurações de Ambiente
FLN_OAUTH_TOKEN = os.getenv("FLN_OAUTH_TOKEN")

# MODO SIMULAÇÃO S-TIER (Projetos de Alto Valor)
SIMULATED_LEADS = [
    {"platform": "freelancer", "desc": "Amazon Scraper with Anti-Bot Bypass and Proxy Rotation"},
    {"platform": "freelancer", "desc": "Automated LinkedIn Lead Generation Bot with AI Personalization"},
    {"platform": "freelancer", "desc": "Complex API Integration between SAP and Custom E-commerce Platform"}
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("SentinelReal")

def sync_to_github():
    """Executa o ciclo de sincronização com o GitHub."""
    logger.info("🔄 Iniciando Sincronização com GitHub...")
    try:
        commands = [
            'git config --global user.email "diego@sniper.bot"',
            'git config --global user.name "Jules Sniper"',
            'git branch -M main',
            'git add output/*.txt',
            "git commit -m 'Sniper Report: Nova proposta gerada' || echo 'Nada para commitar'",
            'git push origin main'
        ]

        for cmd in commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0 and "Nada para commitar" not in result.stdout:
                logger.warning(f"Aviso no comando '{cmd}': {result.stderr.strip()}")

        logger.info("🚀 Loot sincronizado com GitHub!")
    except Exception as e:
        logger.error(f"❌ Erro crítico no Sync: {e}")

def process_radar():
    """Gira o radar em busca de novos alvos."""
    if not os.path.exists("output"):
        os.makedirs("output")

    # Tenta usar o Freelancer SDK se o token estiver presente
    leads = []
    if FLN_OAUTH_TOKEN:
        logger.info("📡 Tentando conexão com Freelancer API...")
        try:
            # Aqui entraria a lógica da freelancersdk
            # Por enquanto, se falhar ou não retornar nada, vai para simulação
            pass
        except Exception as e:
            logger.warning(f"Falha na API: {e}. Ativando MODO SIMULAÇÃO S-TIER.")

    if not leads:
        logger.info("⚠️  Usando MODO SIMULAÇÃO S-TIER (Alvos de Alto Valor)")
        leads = SIMULATED_LEADS

    for i, lead in enumerate(leads):
        desc = lead.get("desc", "")
        logger.info(f"🦅 Alvo Localizado: {desc[:50]}...")

        # Gera a proposta (passando use_ai=True para tentar IA primeiro, fallback automático no gerador)
        proposal = generate_proposal("freelancer", desc, use_ai=True)

        filename = f"output/PROPOSTA_{int(time.time())}_{i}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"TITLE: {desc}\n---\n{proposal}")

        logger.info(f"✅ Proposta salva: {filename}")

        # Sincroniza imediatamente após a geração
        sync_to_github()

def main():
    logger.info("🕵️ Jules Sniper Sentinel Ativado. Radar online.")
    while True:
        process_radar()
        logger.info("💤 Radar em espera (60s)...")
        time.sleep(60)

if __name__ == "__main__":
    main()
