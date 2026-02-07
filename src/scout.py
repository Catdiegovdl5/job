import os
import time
import random
import logging
import sqlite3
import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SESSION_FILE = "data/session.json"
DB_FILE = "data/sniper.db"

class Scout:
    def __init__(self, headless=True):
        self.headless = headless
        self.db_conn = None
        self.init_db()

    def init_db(self):
        try:
            self.db_conn = sqlite3.connect(DB_FILE)
            cursor = self.db_conn.cursor()
            # Ensure LEADS table exists
            cursor.execute('''CREATE TABLE IF NOT EXISTS leads
                              (url TEXT PRIMARY KEY, title TEXT, description TEXT,
                               skills TEXT, budget TEXT, status TEXT DEFAULT 'NEW',
                               created_at TIMESTAMP, score INTEGER DEFAULT 0)''')
            self.db_conn.commit()
        except Exception as e:
            logger.error(f"DB Init Failed: {e}")

    def save_lead(self, lead_data):
        try:
            cursor = self.db_conn.cursor()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''INSERT OR IGNORE INTO leads (url, title, description, skills, budget, created_at)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (lead_data['url'], lead_data['title'], lead_data['description'],
                            lead_data['skills'], lead_data['budget'], timestamp))
            self.db_conn.commit()
            if cursor.rowcount > 0:
                logger.info(f"New Lead Saved: {lead_data['title']}")
                return True
            return False
        except Exception as e:
            logger.error(f"Save Lead Failed: {e}")
            return False

    def run(self):
        logger.info("Starting Scout Mission...")
        storage_state = SESSION_FILE if os.path.exists(SESSION_FILE) else None

        with sync_playwright() as p:
            args = ["--disable-blink-features=AutomationControlled"]
            if self.headless:
                 args.extend(["--headless=new", "--disable-gpu", "--no-sandbox"])

            browser = p.chromium.launch(headless=self.headless, args=args)

            context = browser.new_context(
                storage_state=storage_state,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )

            page = context.new_page()
            stealth = Stealth()
            stealth.use_sync(context)

            try:
                # 1. Search Logic (Freelancer.com Example)
                # Using a generic search URL for "Web Scraping" projects
                search_url = "https://www.freelancer.com/jobs/web-scraping/"
                page.goto(search_url, timeout=60000)

                # Wait for results
                page.wait_for_selector('.JobSearchCard-item', timeout=15000)

                # Extract Project Cards
                cards = page.query_selector_all('.JobSearchCard-item')
                logger.info(f"Found {len(cards)} potential leads.")

                for card in cards[:10]: # Limit to top 10 per run
                    try:
                        title_el = card.query_selector('.JobSearchCard-primary-heading-link')
                        title = title_el.inner_text().strip() if title_el else "Unknown"
                        url = "https://www.freelancer.com" + title_el.get_attribute('href') if title_el else ""

                        desc_el = card.query_selector('.JobSearchCard-primary-description')
                        description = desc_el.inner_text().strip() if desc_el else ""

                        skills_el = card.query_selector('.JobSearchCard-primary-tags')
                        skills = skills_el.inner_text().strip().replace('\n', ', ') if skills_el else ""

                        budget_el = card.query_selector('.JobSearchCard-primary-price')
                        budget = budget_el.inner_text().strip() if budget_el else ""

                        # Basic Filtering
                        if "verified" not in budget.lower() and "$" not in budget:
                            # Strict verification check if desired, skipping for now to get data
                            pass

                        lead = {
                            "title": title,
                            "url": url,
                            "description": description,
                            "skills": skills,
                            "budget": budget
                        }

                        self.save_lead(lead)

                    except Exception as e:
                        logger.warning(f"Error parsing card: {e}")

            except Exception as e:
                logger.error(f"Scout Error: {e}")
            finally:
                browser.close()
                if self.db_conn:
                    self.db_conn.close()

if __name__ == "__main__":
    scout = Scout(headless=True)
    scout.run()
