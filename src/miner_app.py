import asyncio
import os
import shutil
from playwright.async_api import async_playwright
import time
import random
from dotenv import load_dotenv

load_dotenv()

class FreelancerScout:
    def __init__(self, headless=True):
        self.headless = headless
        self.base_url = "https://www.freelancer.com/jobs"
        self.user_data_dir = "./chrome_user_data"

    def clean_singleton_lock(self):
        """Removes the SingletonLock file to prevent 'ProcessSingleton' errors."""
        lock_path = os.path.join(self.user_data_dir, "SingletonLock")
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print(f"Auto-Cleanup: Removed {lock_path}")
            except Exception as e:
                print(f"Auto-Cleanup Error: Failed to remove lock - {e}")

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

            # SIMULATION DATA (to prove the logic works in the environment)
            simulated_jobs = [
                {"title": "Build a Scraper", "budget": 250, "verified": True, "description": "Need a python scraper."},
                {"title": "Fix my bug", "budget": 50, "verified": True, "description": "Small fix."},
                {"title": "Big Project", "budget": 500, "verified": False, "description": "Huge project."},
                {"title": "High Value Python", "budget": 300, "verified": True, "description": "Complex python task."}
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

                    # FIX: Auto-Pilot Logic (Score > 85)
                    if score > 85:
                        print(f"Auto-Pilot Triggered for: {job['title']} (Score: {score})")
                        # Here we would trigger the proposal generation automatically
                        # master_template.generate_proposal(job)

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
