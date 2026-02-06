import json
import os
import re

class MasterTemplate:
    def __init__(self, core_file='turbo_core_v111_final_clean.json'):
        # Ensure path is relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.core_file = os.path.join(base_dir, core_file)
        self.data = self.load_core()

    def load_core(self):
        try:
            with open(self.core_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.core_file} not found.")
            return {}

    def get_template_for_project(self, title, description):
        """
        Selects the best template based on keywords matching the project title/description.
        """
        title_lower = title.lower()
        desc_lower = description.lower()

        best_match = "default"
        max_score = 0

        if 'nucleos' in self.data:
            for nucleus, info in self.data['nucleos'].items():
                score = 0
                for keyword in info.get('keywords', []):
                    if keyword in title_lower or keyword in desc_lower:
                        score += 1

                # Simple heuristic: map nucleus to template key if possible
                # For now, we map 'Data' to 'scraping' template if score is high
                if nucleus == 'Data' and score > 0 and score > max_score:
                    max_score = score
                    best_match = 'scraping'
                elif nucleus == 'Tech' and score > 0 and score > max_score:
                    max_score = score
                    best_match = 'web_dev'

        return self.data.get('templates', {}).get(best_match, "")

    def generate_proposal(self, project_data):
        """
        Generates a proposal and saves it to the WAITING_APPROVAL path.
        project_data: dict with 'title', 'description', etc.
        """
        title = project_data.get('title', 'Untitled')
        description = project_data.get('description', '')

        template_text = self.get_template_for_project(title, description)
        proposal_text = template_text.replace("{project_title}", title)

        # Sanitize title for filename
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")

        # FIX: Correct path prefix WAITING_APPROVAL_ to the filename
        output_dir = "propostas_geradas"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = f"WAITING_APPROVAL_{safe_title}.txt"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(proposal_text)

        print(f"Proposal saved to: {filepath}")
        return filepath

if __name__ == "__main__":
    # Test
    mt = MasterTemplate()
    test_project = {
        "title": "Python Web Scraper Needed",
        "description": "I need a script to scrape data from a website using Selenium or Playwright."
    }
    mt.generate_proposal(test_project)
