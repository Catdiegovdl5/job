import asyncio
import os
import sys
import argparse
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Sync Credentials Logic
load_dotenv()

class FreelancerBidder:
    def __init__(self, headless=True, user=None, password=None):
        self.headless = headless
        self.user = user or os.getenv("FLN_USER") or os.getenv("FREELANCER_EMAIL")
        self.password = password or os.getenv("FLN_PASS") or os.getenv("FREELANCER_PASSWORD")
        self.user_data_dir = "./chrome_user_data"
        self.login_url = "https://www.freelancer.com/login"

    def clean_singleton_lock(self):
        """Removes the SingletonLock file to prevent 'ProcessSingleton' errors."""
        lock_path = os.path.join(self.user_data_dir, "SingletonLock")
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print(f"Auto-Cleanup: Removed {lock_path}")
            except Exception as e:
                print(f"Auto-Cleanup Error: Failed to remove lock - {e}")

    async def run(self, target_url=None):
        if not self.user or not self.password:
            print("Error: Missing Credentials. Set FLN_USER/FLN_PASS in .env or pass args.")
            return

        self.clean_singleton_lock()
        print(f"Starting Bidder for user: {self.user}")

        async with async_playwright() as p:
            # Launch with persistent context if we want to save session, or standard.
            # Using standard for now to be safe in this env.
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            # Timeout Adjustment: 45 seconds
            print("Navigating to login page (Timeout: 45s)...")
            try:
                await page.goto(self.login_url, timeout=45000)

                # Simulation of Login
                # await page.fill('input[name="username"]', self.user)
                # await page.fill('input[name="password"]', self.password)
                # await page.click('button[type="submit"]')
                # await page.wait_for_navigation()

                print("Login simulated.")

                if target_url:
                    print(f"Navigating to Target Job: {target_url}")
                    # await page.goto(target_url, timeout=45000)
                    # Perform bidding logic...

            except Exception as e:
                print(f"Timeout/Error during navigation: {e}")
            finally:
                await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Freelancer Bidder Bot')
    parser.add_argument('--user', help='Freelancer Username/Email')
    parser.add_argument('--password', help='Freelancer Password')
    parser.add_argument('--url', help='Target Job URL')

    args = parser.parse_args()

    bidder = FreelancerBidder(user=args.user, password=args.password)
    asyncio.run(bidder.run(target_url=args.url))
