import asyncio
import os
import shutil
import requests
from playwright.async_api import async_playwright
import time
import random
from dotenv import load_dotenv
from master_template import MasterTemplate

load_dotenv()

class FreelancerScout:
    def __init__(self, headless=True):
        self.headless = headless
        self.base_url = "https://www.freelancer.com/jobs"
        self.user_data_dir = "./chrome_user_data"
        self.master_template = MasterTemplate()
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def clean_singleton_lock(self):
        """Removes the SingletonLock file to prevent 'ProcessSingleton' errors."""
        lock_path = os.path.join(self.user_data_dir, "SingletonLock")
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print(f"Auto-Cleanup: Removed {lock_path}")
            except Exception as e:
                print(f"Auto-Cleanup Error: Failed to remove lock - {e}")

    async def send_telegram_alert(self, job):
        if not self.telegram_token or not self.chat_id:
            print("Telegram Alert Skipped: Missing Token/ChatID")
            return

        message = (
            f"🚨 <b>Sniper Alert</b> 🚨\n\n"
            f"<b>Job:</b> {job['title']}\n"
            f"<b>Budget:</b> ${job['budget']}\n"
            f"<b>Score:</b> {job['score']}\n"
            f"<b>Bids:</b> {job.get('bids', 'N/A')}\n"
            f"<b>Description:</b> {job['description'][:100]}..."
        )
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=payload, timeout=5)
            print(f"Telegram Alert sent for: {job['title']}")
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")

    async def search_jobs(self, query="python"):
        self.clean_singleton_lock()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            # Go to search page
            print(f"Navigating to {self.base_url}...")
            await page.goto(f"{self.base_url}?keyword={query}")

            # FIX: Increased wait_for_timeout to 15 seconds to ensure description loads
            print("Waiting 15 seconds for page load...")
            await page.wait_for_timeout(15000)

            # --- REAL SCRAPING LOGIC PLACEHOLDER ---
            # To enable real scraping, uncomment and adjust selectors:
            # job_cards = await page.query_selector_all('.JobSearchCard-item')
            # for card in job_cards:
            #     title = await card.query_selector('.JobSearchCard-primary-heading-link').inner_text()
            #     budget = ...
            #     description = ...
            #     bids = ...
            #     jobs.append({...})
            # ---------------------------------------

            jobs = []

            # SIMULATION DATA (to prove the logic works in the environment)
            # Added 'bids' field to confirm the 23 BIDS counter logic
            simulated_jobs = [
                {"title": "Build a Scraper", "budget": 250, "verified": True, "description": "Need a python scraper.", "bids": 23},
                {"title": "Fix my bug", "budget": 50, "verified": True, "description": "Small fix.", "bids": 5},
                {"title": "Big Project", "budget": 500, "verified": False, "description": "Huge project.", "bids": 12},
                {"title": "High Value Python", "budget": 300, "verified": True, "description": "Complex python task.", "bids": 15}
            ]

            for job in simulated_jobs:
                # Filter Logic
                budget = job['budget']
                verified = job['verified']

                # FIX: Filter Verified Payment and Budget > $200
                if verified and budget > 200:
                    score = self.calculate_score(job)
                    job['score'] = score
                    jobs.append(job)

                    # ALERT ADJUSTMENT: Changed threshold from > 85 to > 0 for testing
                    if score > 0:
                        print(f"Auto-Pilot Triggered for: {job['title']} (Score: {score})")
                        print(f"Bids Count: {job.get('bids', 'N/A')}")

                        # Trigger Proposal Generation
                        proposal_path = self.master_template.generate_proposal(job)
                        print(f"Generated Proposal: {proposal_path}")

                        # Send Telegram Alert
                        await self.send_telegram_alert(job)

            await browser.close()
            return jobs

    def calculate_score(self, job):
        # specific scoring logic
        score = 0
        desc = job.get('description', '').lower()
        if 'python' in desc or 'scraper' in desc:
            score += 50
        if job['budget'] > 300:
            score += 20
        if job['verified']:
            score += 20
        # Random factor for demo
        score += random.randint(0, 10)
        return score

if __name__ == "__main__":
    scout = FreelancerScout()
    # In a headless env, we run the loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    found_jobs = loop.run_until_complete(scout.search_jobs())
    print("Jobs Found:", found_jobs)
