
import time
import logging
import subprocess
import os
from src.proposal_generator import generate_proposal
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.helpers import create_search_projects_filter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("SentinelReal")

def sync_to_github():
    logger.info("🚀 Enviando alvos reais para o GitHub...")
    try:
        subprocess.run("git add output/*.txt", shell=True)
        subprocess.run("git commit -m 'Sniper Report: Alvos Reais Localizados'", shell=True)
        subprocess.run("git push origin main", shell=True)
        logger.info("✅ Sincronização concluída!")
    except Exception as e:
        logger.warning(f"⚠️ Git Sync: {e}")

def process_radar():
    token = os.environ.get("FLN_OAUTH_TOKEN")
    if not os.path.exists("output"): os.makedirs("output")

    logger.info("📡 CONECTANDO AO RADAR DO FREELANCER.COM...")
    
    try:
        session = Session(oauth_token=token, url="https://www.freelancer.com")
        
        # Filtro de Busca: Projetos de Python, Scraping e Automação
        query = "python scraping automation"
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        
        result = search_projects(session, query=query, search_filter=search_filter)
        
        if result and 'projects' in result:
            projects = result['projects'][:3] # Analisar os 3 mais recentes
            logger.info(f"🎯 {len(projects)} ALVOS REAIS ENCONTRADOS!")
            
            for i, p in enumerate(projects):
                title = p.get('title')
                desc = p.get('preview_description')
                project_id = p.get('id')
                
                logger.info(f"--------------------------------------------------")
                logger.info(f"🎯 ALVO REAL: {title}")
                
                # Inteligência Artificial escrevendo a proposta
                proposal = generate_proposal("freelancer", f"{title}: {desc}", use_ai=True)
                
                filename = f"output/REAL_JOB_{project_id}.txt"
                with open(filename, "w", encoding="utf-8") as f_out:
                    f_out.write(f"ID: {project_id}\nTITLE: {title}\n\n{proposal}")
                
                logger.info(f"✅ Proposta salva: {filename}")
                time.sleep(15) # Evitar 429 na IA
                
            sync_to_github()
        else:
            logger.info("⏳ Nenhum projeto novo encontrado no radar. Tentando novamente em breve.")

    except Exception as e:
        logger.error(f"❌ Falha no Radar Real: {e}")

if __name__ == "__main__":
    process_radar()
