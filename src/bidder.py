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
            # For now, we continue in simulation mode if credentials are missing
            print("Running in SIMULATION MODE due to missing credentials.")

        # If target_url is just a title (passed from miner), try to construct URL
        if target_url and not target_url.startswith("http"):
             target_url = f"https://www.freelancer.com/projects/{target_url.replace(' ', '-').lower()}"

        self.clean_singleton_lock()
        print(f"Starting Bidder for user: {self.user}")
        print(f"Target Job: {target_url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            print("Navigating to Freelancer Login (Timeout: 45s)...")
            try:
                # Real Login Logic (Commented out to prevent blocking/captcha in headless if not configured properly)
                # await page.goto(self.login_url, timeout=45000)
                # await page.fill('input[name="username"]', self.user)
                # await page.fill('input[name="password"]', self.password)
                # await page.click('button[type="submit"]')
                # await page.wait_for_navigation()

                # Simulation Logic
                print(">> [SIMULATION] Login Successful.")
                print(f">> [SIMULATION] Navigating to Project: {target_url}")

                # Here we would load the generated proposal from file
                # But since we don't have the filename passed directly, we simulate
                print(">> [SIMULATION] Loading Proposal Text...")
                print(">> [SIMULATION] Pasting Proposal into Bid Form...")
                print(">> [SIMULATION] Clicking 'Place Bid'...")

                print("✅ BID PLACED SUCCESSFULLY (Simulated)")

            except Exception as e:
                print(f"Error during bidder execution: {e}")
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
