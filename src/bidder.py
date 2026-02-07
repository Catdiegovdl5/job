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
        # Credential Fallback (Priority: User Arg > FLN_USER > FREELANCER_EMAIL)
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
                print(f"[GUARDRAIL] Auto-Cleanup: Removed {lock_path}")
            except Exception as e:
                print(f"[GUARDRAIL] Auto-Cleanup Error: Failed to remove lock - {e}")

    def parse_proposal_file(self, filepath):
        """Reads the proposal file to extract URL and Text."""
        url = None
        proposal_text = ""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Assuming first line *might* be URL if properly formatted,
                # but currently master_template doesn't write URL there.
                # If we rely on filename for URL construction, we can do that.
                proposal_text = "".join(lines)

                # Try to find URL inside text if master_template puts it there?
                # For now, let's assume URL is passed via args OR constructed from filename
        except Exception as e:
            print(f"Error reading proposal file: {e}")
        return url, proposal_text

    async def run(self, target_url=None, proposal_file=None):
        # [GUARDRAIL] Clean SingletonLock before every run
        self.clean_singleton_lock()

        if not self.user or not self.password:
            print("Error: Missing Credentials. Set FLN_USER/FLN_PASS in .env or pass args.")
            # Continue in simulation mode
            print("[SIMULATION] Running without credentials.")

        proposal_text = ""
        if proposal_file:
            print(f"Loading proposal from: {proposal_file}")
            _, proposal_text = self.parse_proposal_file(proposal_file)

            # If target_url wasn't provided, try to infer from filename?
            # Filename format: WAITING_APPROVAL_{title}.txt
            if not target_url:
                filename = os.path.basename(proposal_file)
                if filename.startswith("WAITING_APPROVAL_"):
                    title_part = filename.replace("WAITING_APPROVAL_", "").replace(".txt", "")
                    target_url = f"https://www.freelancer.com/projects/{title_part.replace('_', '-').lower()}"

        # Fallback URL construction if just a title string
        if target_url and not target_url.startswith("http"):
             target_url = f"https://www.freelancer.com/projects/{target_url.replace(' ', '-').lower()}"

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

                if proposal_text:
                    print(">> [SIMULATION] Proposal Text Loaded (Preview):")
                    print(proposal_text[:100] + "...")
                else:
                    print(">> [SIMULATION] No Proposal Text Loaded (Generic Bid)")

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
    parser.add_argument('--url', help='Target Job URL (Optional if file provided)')
    parser.add_argument('--file', help='Path to proposal file (.txt)')

    args = parser.parse_args()

    bidder = FreelancerBidder(user=args.user, password=args.password)
    asyncio.run(bidder.run(target_url=args.url, proposal_file=args.file))
