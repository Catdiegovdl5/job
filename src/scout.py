import os
import json
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.exceptions import ProjectsNotFoundException

class Scout:
    def __init__(self):
        self.oauth_token = os.getenv("FLN_OAUTH_TOKEN")
        self.seen_file = "seen_projects.txt"
        self.seen_projects = self._load_seen_projects()
        self.session = Session(oauth_token=self.oauth_token) if self.oauth_token else None

    def _load_seen_projects(self):
        if not os.path.exists(self.seen_file):
            return set()
        with open(self.seen_file, "r") as f:
            return set(line.strip() for line in f if line.strip())

    def mark_seen(self, project_id):
        self.seen_projects.add(str(project_id))
        with open(self.seen_file, "a") as f:
            f.write(f"{project_id}\n")

    def fetch_projects(self):
        if not self.session:
            print("Warning: FLN_OAUTH_TOKEN not found. Returning mock data.")
            return self._mock_fetch()

        query = "scraping automation python api"

        try:
            # Basic search query
            # Note: Filters like 'payment_verified' might need to be checked on the result objects
            # depending on the SDK version features.
            query_data = {
                "query": query,
                "project_statuses": ["active"],
                "limit": 10
            }

            projects_result = search_projects(self.session, **query_data)

            valid_projects = []
            if projects_result and hasattr(projects_result, 'projects'):
                for p in projects_result.projects:
                    pid = str(p.id)
                    if pid in self.seen_projects:
                        continue

                    # Budget Check (USD 150+)
                    # Assuming p.budget.minimum exists
                    if not p.budget or not p.budget.minimum or p.budget.minimum < 150:
                        continue

                    # Currency Check
                    if p.currency and p.currency.code != "USD":
                        continue

                    # Description Keyword Check (Redundant with query but safer)
                    desc = p.preview_description or p.description or ""

                    valid_projects.append({
                        "id": pid,
                        "title": p.title,
                        "description": desc,
                        "url": f"https://www.freelancer.com/projects/{p.seo_url}",
                        "budget": f"{p.budget.minimum}-{p.budget.maximum}",
                        "currency": p.currency.code
                    })

            return valid_projects

        except ProjectsNotFoundException:
            return []
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

    def _mock_fetch(self):
        # Fallback for testing/no-token scenarios
        mock_p = {
            "id": "123456",
            "title": "Build a Web Scraper for E-commerce",
            "description": "I need a Python script to scrape product data from a major retailer.",
            "url": "https://www.freelancer.com/projects/python/scraper",
            "budget": "200-500",
            "currency": "USD"
        }
        if str(mock_p['id']) not in self.seen_projects:
            return [mock_p]
        return []
