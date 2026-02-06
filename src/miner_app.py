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
        # Load weights from master template's data source for efficiency, or just use master_template to query
        self.weights_data = self.master_template.data

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
            f"<b>Rate:</b> ${job.get('hourly_rate', 0)}/hr\n"
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

            # SIMULATION DATA UPDATED FOR OCEANO AZUL TESTING
            simulated_jobs = [
                {"title": "Migration Script", "budget": 250, "verified": True, "description": "Need to migrate database.", "bids": 5, "hourly_rate": 50}, # High score (Migration + Rate)
                {"title": "Simple Scraping", "budget": 50, "verified": True, "description": "Just scraping.", "bids": 5, "hourly_rate": 20}, # Low budget, ignored
                {"title": "Crowded Project", "budget": 500, "verified": True, "description": "Huge project.", "bids": 20, "hourly_rate": 60}, # Ignored (> 15 bids)
                {"title": "API Integration", "budget": 300, "verified": True, "description": "Complex API integration.", "bids": 10, "hourly_rate": 45} # High score (API + Rate)
            ]

            for job in simulated_jobs:
                # 1. Filter: Verified Payment
                if not job.get('verified'):
                    continue

                # 2. Filter: Budget > $200
                if job.get('budget', 0) <= 200:
                    continue

                # 3. Filter: Ignore jobs with > 15 bids
                if job.get('bids', 0) > 15:
                    print(f"Ignored Crowded Job: {job['title']} ({job['bids']} bids)")
                    continue

                # Calculate Score
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
        score = 0
        desc = job.get('description', '').lower()
        title = job.get('title', '').lower()

        # 1. Base Logic (from previous version, updated with JSON weights if available)
        # We read from self.weights_data['nucleos']
        nucleos = self.weights_data.get('nucleos', {})

        for nucleus_name, data in nucleos.items():
            keywords = data.get('keywords', [])
            weight = data.get('weight', 1) # Default weight 1 if not specified (Data/Tech/Marketing)

            # Check for matches
            for kw in keywords:
                if kw in desc or kw in title:
                    score += (10 * weight) # Multiply by weight factor
                    # Break after one match per nucleus? Or accumulate? Accumulating for now.

        # 2. Hourly Rate Boost (Priorize projects with Hourly Rate > $40/hr)
        if job.get('hourly_rate', 0) > 40:
            score += 30 # Significant boost

        # 3. Verified Payment Boost
        if job.get('verified'):
            score += 20

        return score

if __name__ == "__main__":
    scout = FreelancerScout()
    # In a headless env, we run the loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    found_jobs = loop.run_until_complete(scout.search_jobs())
    print("Jobs Found:", found_jobs)
