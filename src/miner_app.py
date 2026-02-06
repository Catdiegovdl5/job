import asyncio
import os
import shutil
import requests
import json
from playwright.async_api import async_playwright
import time
import random
import re
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
        # Load weights from master template's data source
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

    def get_proposal_content(self, title):
        # Sanitize title to match filename generation logic
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
        filename = f"WAITING_APPROVAL_{safe_title}.txt"
        filepath = os.path.join("propostas_geradas", filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "(Proposal file not found)"

    async def send_telegram_alert(self, job):
        if not self.telegram_token or not self.chat_id:
            print("Telegram Alert Skipped: Missing Token/ChatID")
            return

        # Prepare summary/translation (Mocking translation by just prepending label)
        translated_title = f"{job['title']} (Resumo PT-BR: Oportunidade em {job['title']})"
        proposal_content = self.get_proposal_content(job['title'])

        message = (
            f"🚨 <b>Sniper Alert</b> 🚨\n\n"
            f"<b>Job:</b> {translated_title}\n"
            f"<b>Budget:</b> ${job['budget']}\n"
            f"<b>Rate:</b> ${job.get('hourly_rate', 0)}/hr\n"
            f"<b>Score:</b> {job['score']}\n"
            f"<b>Bids:</b> {job.get('bids', 'N/A')}\n\n"
            f"<b>Proposta Gerada:</b>\n<pre>{proposal_content}</pre>"
        )

        # Interactive Buttons
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Aprovar", "callback_data": f"approve_bid|{job['title']}"},
                    {"text": "❌ Rejeitar", "callback_data": f"reject_bid|{job['title']}"}
                ]
            ]
        }

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "reply_markup": keyboard
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

            jobs = []

            # SIMULATION DATA UPDATED FOR 'LUCRO RAPIDO' TESTING
            simulated_jobs = [
                {"title": "Excel VBA Macro", "budget": 160, "verified": True, "description": "Need a vba macro for excel.", "bids": 5, "hourly_rate": 0},
                {"title": "Zapier Automation", "budget": 250, "verified": True, "description": "Connect sheets to email via Zapier.", "bids": 2, "hourly_rate": 0},
                {"title": "Google Maps Scraper", "budget": 200, "verified": True, "description": "Scrape google maps data.", "bids": 3, "hourly_rate": 0},
                {"title": "Crowded Migration", "budget": 500, "verified": True, "description": "Data migration.", "bids": 12, "hourly_rate": 60},
                {"title": "Low Budget Scraper", "budget": 100, "verified": True, "description": "Simple scraping.", "bids": 0, "hourly_rate": 0}
            ]

            global_settings = self.weights_data.get('global_settings', {})
            min_budget = global_settings.get('min_budget', 150)
            max_bids = global_settings.get('max_bids', 10)

            for job in simulated_jobs:
                # 1. Filter: Verified Payment
                if not job.get('verified'):
                    continue

                # 2. Filter: Budget > $150
                if job.get('budget', 0) <= min_budget:
                    continue

                # 3. Filter: Ignore jobs with > 10 bids
                if job.get('bids', 0) > max_bids:
                    print(f"Ignored Crowded Job: {job['title']} ({job['bids']} bids)")
                    continue

                # Calculate Score
                score = self.calculate_score(job)
                job['score'] = score
                jobs.append(job)

                # ALERT ADJUSTMENT: Changed threshold from >= 5 to > 0
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

        # 1. Base Logic (Nucleos from JSON)
        nucleos = self.weights_data.get('nucleos', {})

        for nucleus_name, data in nucleos.items():
            keywords = data.get('keywords', [])
            weight = data.get('weight', 1)

            # Check for matches
            for kw in keywords:
                if kw in desc or kw in title:
                    score += (10 * weight) # Base multiplier

        # 2. Hourly Rate Boost (Priorize projects with Hourly Rate > $40/hr)
        if job.get('hourly_rate', 0) > 40:
            score += 30

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
