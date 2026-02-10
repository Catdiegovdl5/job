import time
import sys
import os
from datetime import datetime

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scout import Scout
from src.ai_client import AIClient
from src.telegram_bot import TelegramCommander

POLL_INTERVAL = 900  # 15 minutes

def run_cycle(scout, ai, commander):
    print(f"--- Starting Sentinel Cycle at {datetime.now()} ---")
    projects = scout.fetch_projects()
    print(f"Found {len(projects)} new potential projects.")

    for project in projects:
        print(f"Processing project: {project.get('title', 'Unknown')}")

        # Generate Proposal
        proposal = ai.generate(project.get('description', ''), 'freelancer')

        # Send Alert
        commander.send_alert(project, proposal)

        # Mark as Seen
        scout.mark_seen(project['id'])

    print("--- Cycle Complete ---")

def main():
    print("Initializing JULES Sniper S-Tier: ONLINE")

    try:
        scout = Scout()
        ai = AIClient()
        commander = TelegramCommander()
    except Exception as e:
        print(f"Critical Error during initialization: {e}")
        return

    while True:
        try:
            run_cycle(scout, ai, commander)
        except Exception as e:
            print(f"Error in cycle: {e}")

        print(f"Sleeping for {POLL_INTERVAL} seconds...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
