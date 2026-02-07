import asyncio
import os
import shutil
import requests
import json
from playwright.async_api import async_playwright
import time
import random
import re
import html
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
            print(f"Telegram Alert Skipped: Missing Token/ChatID. Please configure .env.")
            return

        # Prepare summary/translation (Mocking translation by just prepending label)
        # Escape HTML characters to prevent 'Bad Request' errors
        safe_title = html.escape(job['title'])
        translated_title = f"{safe_title} (Resumo PT-BR: Oportunidade em {safe_title})"
        proposal_content = html.escape(self.get_proposal_content(job['title']))

        # Determine link based on title (URL construction for Freelancer.com usually follows title slug)
        # This is a heuristic; ideal would be to scrape the actual link.
        job_link = f"https://www.freelancer.com/projects/{job['title'].replace(' ', '-').lower()}"

        message = (
            f"🚨 <b>Sniper Alert</b> 🚨\n\n"
            f"<b>Job:</b> <a href='{job_link}'>{translated_title}</a>\n"
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
                    {"text": "✅ Aprovar (Enviar Proposta)", "callback_data": f"approve_bid|{job['title']}"},
                    {"text": "❌ Rejeitar", "callback_data": f"reject_bid|{job['title']}"}
                ]
            ]
        }

        # Check for potential 'bot' prefix duplication in token
        token = self.telegram_token
        if token.startswith("bot"):
            print("Warning: Token starts with 'bot', this might be duplicated in URL construction.")

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        print(f"[DEBUG] Telegram URL: {url.replace(token, 'TOKEN_HIDDEN')}")

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        }

        try:
            print(f"Sending Telegram Alert for: {job['title']}")
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"Telegram Alert sent successfully.")
            else:
                print(f"Failed to send Telegram alert: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception sending Telegram alert: {e}")

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

            # Attempt to scrape real jobs
            scraped_jobs = []
            try:
                # Freelancer.com specific selectors (Project Cards)
                job_cards = await page.locator(".JobSearchCard-item").all()
                print(f"[Scraper] Found {len(job_cards)} job cards on page.")

                for card in job_cards:
                    try:
                        title = await card.locator(".JobSearchCard-primary-heading-link").inner_text()
                        description = await card.locator(".JobSearchCard-primary-description").inner_text()

                        # Budget Parsing
                        budget_text = await card.locator(".JobSearchCard-primary-price").inner_text()
                        # Clean budget string (e.g., "$250 - $750 USD" -> 250)
                        budget_text_clean = re.sub(r"[^\d\-]", "", budget_text.split("-")[0])
                        budget = int(budget_text_clean) if budget_text_clean else 0

                        # Bids Parsing
                        bids_text = await card.locator(".JobSearchCard-secondary-entry:has-text('bids')").inner_text()
                        bids = int(re.sub(r"[^\d]", "", bids_text)) if bids_text else 0

                        # Verified Check
                        verified = await card.locator(".JobSearchCard-primary-heading-status-verified").count() > 0

                        # Hourly Rate Check (heuristic)
                        is_hourly = "hr" in budget_text.lower()
                        hourly_rate = budget if is_hourly else 0

                        job_data = {
                            "title": title.strip(),
                            "budget": budget,
                            "verified": verified,
                            "description": description.strip(),
                            "bids": bids,
                            "hourly_rate": hourly_rate
                        }
                        scraped_jobs.append(job_data)
                    except Exception as e:
                        print(f"[Scraper] Error parsing card: {e}")
                        continue

            except Exception as e:
                print(f"[Scraper] Error during scraping: {e}")

            # Fallback to simulation if no jobs found (e.g., login wall or selector change)
            if not scraped_jobs:
                print("[Scraper] No jobs scraped (Login Wall?). Using Simulation Mode.")
                scraped_jobs = [
                    {"title": "Excel VBA Macro", "budget": 160, "verified": True, "description": "Need a vba macro for excel.", "bids": 5, "hourly_rate": 0},
                    {"title": "Zapier Automation", "budget": 250, "verified": True, "description": "Connect sheets to email via Zapier.", "bids": 2, "hourly_rate": 0},
                    {"title": "Google Maps Scraper", "budget": 200, "verified": True, "description": "Scrape google maps data.", "bids": 3, "hourly_rate": 0},
                    {"title": "Crowded Migration", "budget": 500, "verified": True, "description": "Data migration.", "bids": 12, "hourly_rate": 60},
                    {"title": "Low Budget Scraper", "budget": 100, "verified": True, "description": "Simple scraping.", "bids": 0, "hourly_rate": 0}
                ]

            global_settings = self.weights_data.get('global_settings', {})
            min_budget = global_settings.get('min_budget', 150)
            max_bids = global_settings.get('max_bids', 10)

            for job in scraped_jobs:
                # 1. Filter: Verified Payment
                if not job.get('verified'):
                    print(f"Ignored Unverified: {job['title']}")
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

                # ALERT ADJUSTMENT: Changed threshold to >= 0 to force alerts even for score 0
                if score >= 0:
                    print(f"Auto-Pilot Triggered for: {job['title']} (Score: {score})")
                    print(f"Bids Count: {job.get('bids', 'N/A')}")

                    # Trigger Proposal Generation
                    proposal_path = self.master_template.generate_proposal(job)
                    print(f"Generated Proposal: {proposal_path}")

                    # Add to Pending Jobs (GUI Approval)
                    self.add_to_pending_jobs(job)

                    # Send Telegram Alert (Notification Only)
                    await self.send_telegram_alert(job)

    def add_to_pending_jobs(self, job):
        """Adds the job to pending_jobs.json for GUI approval."""
        file_path = "pending_jobs.json"
        try:
            jobs = []
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    try:
                        jobs = json.load(f)
                    except json.JSONDecodeError:
                        jobs = []

            # Check for duplicates
            if not any(j['title'] == job['title'] for j in jobs):
                jobs.append(job)
                with open(file_path, "w") as f:
                    json.dump(jobs, f, indent=4)
                print(f"Job added to Pending Queue: {job['title']}")
            else:
                print(f"Job already in Pending Queue: {job['title']}")

        except Exception as e:
            print(f"Error saving to pending_jobs.json: {e}")

            await browser.close()
            return jobs

    def calculate_score(self, job):
        score = 0
        desc = job.get('description', '').lower()
        title = job.get('title', '').lower()

        # Debug Score
        print(f"\n[DEBUG Score] Checking Job: {title}")

        # 1. Base Logic (Nucleos from JSON)
        nucleos = self.weights_data.get('nucleos', {})

        for nucleus_name, data in nucleos.items():
            keywords = [k.lower() for k in data.get('keywords', [])]
            weight = data.get('weight', 1)

            # Check for matches
            for kw in keywords:
                if kw in desc or kw in title:
                    points = (10 * weight)
                    score += points # Base multiplier
                    print(f"  -> Match ({nucleus_name}): {kw} (+{points})")

        # 2. Hourly Rate Boost (Priorize projects with Hourly Rate > $40/hr)
        if job.get('hourly_rate', 0) > 40:
            score += 30
            print("  -> Hourly Rate Boost (+30)")

        # 3. Verified Payment Boost
        if job.get('verified'):
            score += 20
            print("  -> Verified Payment Boost (+20)")

        if score == 0:
             print("  -> Nucleus Unknown (No keywords matched)")

        return score

if __name__ == "__main__":
    scout = FreelancerScout()
    # In a headless env, we run the loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    found_jobs = loop.run_until_complete(scout.search_jobs())
    print("Jobs Found:", found_jobs)
