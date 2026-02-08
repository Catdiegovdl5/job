import unittest
from src.scout import calculate_cash_score

class TestScout(unittest.TestCase):

    def test_high_priority_score(self):
        title = "Need an Excel VBA Expert"
        desc = "Automate my spreadsheet"
        # VBA (+30)
        score = calculate_cash_score(title, desc)
        # Should be at least 30. If 'Automate' matches 'Automation', maybe +30 more?
        # My implementation checks "automation" in text. "Automate" != "automation".
        # Let's check the implementation:
        # keywords: ["vba", "sql", "seo", "chatbot", "automation"]
        # "Excel" is medium (+15).
        # "VBA" is high (+30).
        # Total should be 45.
        self.assertEqual(score, 45)

    def test_medium_priority_score(self):
        title = "Data Entry Job"
        desc = "Simple writing task"
        # "Data Entry" (+15)
        # "Writing" (+15)
        # Total 30
        score = calculate_cash_score(title, desc)
        self.assertEqual(score, 30)

    def test_mixed_score(self):
        title = "SQL Database for SEO"
        desc = "Writing queries"
        # SQL (+30)
        # SEO (+30)
        # Writing (+15)
        # Total 75
        score = calculate_cash_score(title, desc)
        self.assertEqual(score, 75)

    def test_no_match(self):
        title = "Graphic Design"
        desc = "Make a logo"
        score = calculate_cash_score(title, desc)
        self.assertEqual(score, 0)

if __name__ == "__main__":
    unittest.main()
