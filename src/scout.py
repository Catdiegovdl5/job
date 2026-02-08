from .config import KEYWORDS

def calculate_cash_score(project_title, description):
    """
    Calculates the 'Cash Score' of a lead based on keyword matching.

    Weights:
    - +30 points: VBA, SQL, SEO, Chatbot, Automation (High Priority)
    - +15 points: Writing, Excel, Data Entry (Medium Priority)

    Args:
        project_title (str): Title of the project.
        description (str): Description of the project.

    Returns:
        int: The calculated score.
    """
    score = 0
    text = (project_title + " " + description).lower()

    high_priority_keywords = ["vba", "sql", "seo", "chatbot", "automation"]
    medium_priority_keywords = ["writing", "excel", "data entry"]

    for kw in high_priority_keywords:
        if kw in text:
            score += 30

    for kw in medium_priority_keywords:
        if kw in text:
            score += 15

    return score

class Scout:
    def __init__(self):
        # In a real implementation, this would initialize Playwright
        pass

    def assess_lead(self, lead):
        """
        Assesses a lead and assigns a score.
        """
        title = lead.get("title", "")
        desc = lead.get("description", "")
        score = calculate_cash_score(title, desc)
        return score
