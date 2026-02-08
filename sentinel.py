import os
import logging
from src.proposal_generator import generate_proposal
from src.config import SIMULATED_LEADS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("Sentinel")

def process_leads():
    # Carrega leads simulados (Futuramente aqui entra o RSS do Freelancer)
    leads = SIMULATED_LEADS

    # Cria pasta se não existir
    if not os.path.exists("propostas_geradas"):
        os.makedirs("propostas_geradas")

    # Limpa propostas antigas para evitar confusão
    for f in os.listdir("propostas_geradas"):
        if f.startswith("WAITING_APPROVAL"):
            os.remove(os.path.join("propostas_geradas", f))

    for i, lead in enumerate(leads):
        platform = lead.get("platform", "unknown").lower()

        # Filtro Absoluto: Só Freelancer.com
        if "freelancer" not in platform:
            continue

        desc = lead.get("desc", "")

        # Gera a proposta
        proposal = generate_proposal(platform, desc, use_ai=True)

        # Salva o arquivo pronto para o Bidder
        filename = f"propostas_geradas/WAITING_APPROVAL_lead_{i}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"CORE: FREELANCER_ELITE\n")
            f.write(f"SCORE: 99\n")
            f.write(f"TITLE: {desc[:60]}\n")
            f.write(f"URL: https://www.freelancer.com/projects/fake/project-{i}\n")
            f.write("---\n")
            f.write(proposal)

        logger.info(f"✅ Munição Pronta: {filename}")

if __name__ == "__main__":
    process_leads()
