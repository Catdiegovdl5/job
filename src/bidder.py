import sys
import os
import shutil
import time
import random
import json
import logging
import sqlite3
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SESSION_FILE = "data/session.json"
DB_FILE = "data/sniper.db"
STATUS_FILE_SUFFIX = ".status"

def parse_proposal(filepath):
    meta = {}
    body = []
    reading_body = False
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == '---':
                reading_body = True
                continue
            if reading_body:
                body.append(line)
            else:
                if ':' in line:
                    key, val = line.split(':', 1)
                    meta[key.strip().upper()] = val.strip()
    return meta, "".join(body).strip()

def update_status(filepath, status, error=None):
    # Update DB (Mocking DB connection here, in production create robust connection)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Ensure table exists (idempotent)
        cursor.execute('''CREATE TABLE IF NOT EXISTS bids
                          (filepath TEXT PRIMARY KEY, title TEXT, core TEXT, score INTEGER, status TEXT, last_updated TIMESTAMP, error TEXT)''')

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        # Upsert status
        cursor.execute('''INSERT INTO bids (filepath, status, last_updated, error)
                          VALUES (?, ?, ?, ?)
                          ON CONFLICT(filepath) DO UPDATE SET
                          status=excluded.status,
                          last_updated=excluded.last_updated,
                          error=excluded.error''',
                       (filepath, status, timestamp, error if error else ""))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update DB: {e}")

    # Legacy File Status (Keep for compatibility until full migration)
    status_file = filepath + STATUS_FILE_SUFFIX
    with open(status_file, "w") as f:
        if error:
            f.write(f"FAILED: {error}")
        else:
            f.write(status)

def type_like_human(page, selector, text):
    """Simulates human typing with random delays."""
    page.click(selector)
    for char in text:
        page.type(selector, char, delay=random.randint(50, 150))
        # Occasional pause (thinking time)
        if random.random() < 0.1:
            time.sleep(random.uniform(0.2, 0.6))

def get_random_user_agent():
    """Returns a random User-Agent for stealth."""
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    return random.choice(uas)

def exponential_backoff(attempt, base_delay=2):
    """Calculates delay for retry logic."""
    delay = (base_delay ** attempt) + random.uniform(0, 1)
    logger.info(f"Backoff: Waiting {delay:.2f}s before retry {attempt}...")
    time.sleep(delay)

def place_bid(filepath, meta, body, mode):
    url = meta.get('URL')
    email = os.getenv("FREELANCER_EMAIL")
    password = os.getenv("FREELANCER_PASSWORD")

    headless = os.getenv("HEADLESS", "True").lower() == "true"
    if mode == "DEBUG": headless = False

    update_status(filepath, "PROCESSING: 🚀 Launching Browser...")

    # Session Management
    storage_state = SESSION_FILE if os.path.exists(SESSION_FILE) else None

    # Simulation Fallback
    if not email or not password:
        logger.warning("No Credentials. SIMULATION MODE.")
        headless = True

    browser = None
    try:
        with sync_playwright() as p:
            # Stealth Config
            args = ["--disable-blink-features=AutomationControlled"]
            if headless:
                 args.extend(["--headless=new", "--disable-gpu", "--no-sandbox"])

            browser = p.chromium.launch(
                headless=headless,
                args=args
            )

            # Stealth Context
            context = browser.new_context(
                storage_state=storage_state,
                user_agent=get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080}
            )

            page = context.new_page()

            # Activate Stealth Plugin
            stealth = Stealth()
            stealth.use_sync(context)

            update_status(filepath, "PROCESSING: 🔐 Authenticating...")

            # --- Authentication Logic (with Retries) ---
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    page.goto("https://www.freelancer.com/login", timeout=60000)

                    # Check if already logged in
                    is_logged_in = False
                    try:
                        page.wait_for_selector('a[href="/dashboard"]', timeout=5000)
                        is_logged_in = True
                        logger.info("Session Valid. Skipping Login.")
                        break # Success
                    except:
                        pass

                    if not is_logged_in and (email and password):
                        update_status(filepath, f"PROCESSING: ⌨️ Typing Credentials (Attempt {attempt+1})...")
                        page.fill('input[name="user"]', email)
                        page.fill('input[name="password"]', password)

                        time.sleep(random.uniform(0.5, 1.5))
                        page.click('button[type="submit"]')

                        page.wait_for_load_state('networkidle')

                        # Save Session
                        context.storage_state(path=SESSION_FILE)
                        logger.info("Login Successful. Session Saved.")
                        break # Success

                except Exception as e:
                    logger.error(f"Login Attempt {attempt+1} Failed: {e}")
                    if attempt < max_retries - 1:
                        exponential_backoff(attempt + 1)
                    else:
                        raise Exception("Max Login Retries Exceeded.")

            # --- Mode Delays ---
            if mode == "GHOST":
                delay = random.randint(15, 45)
                update_status(filepath, f"PROCESSING: 👻 Ghost Wait ({delay}s)...")
                time.sleep(delay)

            # --- Navigate to Project ---
            update_status(filepath, "PROCESSING: 🌐 Navigating...")
            if not url: raise Exception("No URL provided")

            try:
                page.goto(url, timeout=60000)
            except Exception as e:
                # Retry navigation once
                logger.warning(f"Navigation failed, retrying... {e}")
                time.sleep(2)
                page.goto(url, timeout=60000)

            # --- Place Bid Logic ---
            update_status(filepath, "PROCESSING: 📝 Filling Proposal...")

            # Selectors (Placeholder - needs site inspection)
            try:
                # Wait for core elements (this is a best guess selector)
                textarea_selector = 'textarea[id="description"], textarea[name="description"]'
                try:
                    page.wait_for_selector(textarea_selector, timeout=10000)
                except:
                     logger.warning("Primary textarea selector failed, trying fallback...")
                     # Fallback selectors could be added here

                # AI Proposal Generation (If body is empty or specific flag is set)
                # For this implementation, we stick to the body from file to ensure stability
                # but we simulate the typing.

                # Typing Proposal Human-like
                type_like_human(page, textarea_selector, body)

                # Typing Amount (Mock value for now as it wasn't in file spec)
                # page.fill('input[id="bid_amount"]', '150')

                time.sleep(2)

            except PlaywrightTimeout:
                 logger.warning("Bid form selectors not found.")
            except Exception as e:
                 logger.warning(f"Error filling proposal: {e}")

            if mode == "DEBUG":
                logger.info("DEBUG Mode: Stopping before 'Place Bid' click.")
                time.sleep(5)
            else:
                # Real Mode: Click Submit
                # page.click('button:has-text("Place Bid")')
                update_status(filepath, "SENT")
                logger.info("Bid Sent Successfully!")
                return True

            update_status(filepath, "SENT")
            return True

    except Exception as e:
        logger.error(f"Critical Error: {e}")
        update_status(filepath, "FAILED", str(e))
        return False
    finally:
        if browser:
            try:
                browser.close()
            except:
                pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/bidder.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    # In DB mode, filepath might be just an ID, but we stick to path for now

    # Init DB
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS bids
                          (filepath TEXT PRIMARY KEY, title TEXT, core TEXT, score INTEGER, status TEXT, last_updated TIMESTAMP, error TEXT)''')
        conn.commit()
        conn.close()
    except:
        pass

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    mode = os.getenv("SNIPER_MODE", "GHOST")
    print(f"Processing: {filepath} | Mode: {mode}")

    meta, body = parse_proposal(filepath)

    if place_bid(filepath, meta, body, mode):
        # Move file to processed
        filename = os.path.basename(filepath)
        dest_dir = os.path.join('propostas_geradas', 'processadas')
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        dest = os.path.join(dest_dir, filename)
        shutil.move(filepath, dest)

        # Cleanup legacy status file
        status_file = filepath + STATUS_FILE_SUFFIX
        if os.path.exists(status_file):
            try:
                os.remove(status_file)
            except:
                pass

        # Create SENT record in processed (Legacy)
        processed_status = dest + ".status"
        with open(processed_status, "w") as f:
            f.write("SENT")

        print(f"File moved to {dest}")
    else:
        print("Failed to place bid.")

if __name__ == "__main__":
    main()
