import os
import json
import logging
from datetime import datetime
from src.proposal_generator import generate_proposal
from src.config import SIMULATED_LEADS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Sentinel")

def fetch_leads():
    """
    Fetches leads from 'leads_input.json' if it exists, otherwise uses simulated leads.
    """
    input_file = "leads_input.json"
    if os.path.exists(input_file):
        try:
            with open(input_file, "r", encoding='utf-8') as f:
                leads = json.load(f)
            logger.info(f"Loaded {len(leads)} leads from {input_file}.")
            return leads
        except Exception as e:
            logger.error(f"Error reading {input_file}: {e}. Falling back to simulation.")

    logger.info("Using simulated leads.")
    return SIMULATED_LEADS

def process_leads():
    """
    Orchestrates the lead processing: Fetch -> Generate -> Save.
    """
    leads = fetch_leads()
    results = []

    for lead in leads:
        platform = lead.get("platform", "unknown")
        desc = lead.get("desc") or lead.get("description", "")
        questions = lead.get("questions")

        if not desc:
            logger.warning(f"Skipping lead for {platform}: No description provided.")
            continue

        logger.info(f"Processing lead for {platform}...")
        try:
            # Always try to use AI first (handled by generate_proposal with use_ai=True)
            proposal = generate_proposal(platform, desc, questions, use_ai=True)

            results.append({
                "timestamp": datetime.now().isoformat(),
                "platform": platform,
                "description": desc,
                "proposal": proposal
            })
        except Exception as e:
            logger.error(f"Failed to process lead for {platform}: {e}")

    output_file = "leads_ready.json"
    try:
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully processed {len(results)} leads. Results saved to {output_file}.")
    except Exception as e:
        logger.error(f"Failed to save results to {output_file}: {e}")

if __name__ == "__main__":
    process_leads()
