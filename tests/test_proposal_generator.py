import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add root to sys.path so we can import src as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.proposal_generator import generate_proposal, detect_skill

class TestProposalGenerator(unittest.TestCase):

    def test_freelancer_proposal_template(self):
        desc = "Need a video for my website"
        proposal = generate_proposal("freelancer", desc, use_ai=False)
        self.assertIn("### Proposal for Freelancer.com", proposal)
        self.assertIn("Pipeline Veo 3", proposal)
        self.assertIn("Test Keywords", proposal)
        self.assertIn("Language: English", proposal)

    def test_99freelas_proposal_template(self):
        desc = "Preciso de tráfego pago"
        proposal = generate_proposal("99freelas", desc, use_ai=False)
        self.assertIn("### Proposta para 99Freelas", proposal)
        self.assertIn("Projeto Piloto", proposal)
        self.assertIn("Idioma: Português", proposal)

    def test_upwork_proposal_template(self):
        desc = "Looking for an SEO expert"
        questions = ["How do you handle SEO?"]
        proposal = generate_proposal("upwork", desc, questions, use_ai=False)
        self.assertIn("### Proposal for Upwork", proposal)
        self.assertIn("Screening Questions", proposal)
        self.assertIn("GEO (Generative Engine Optimization)", proposal)

    def test_invalid_platform(self):
        proposal = generate_proposal("invalid", "test", use_ai=False)
        self.assertIn("Error: Unsupported platform", proposal)

    @patch('src.proposal_generator.GEMINI_API_KEY', 'fake_key')
    @patch('src.proposal_generator.JulesAI')
    def test_ai_generation_success(self, mock_jules_ai):
        mock_client = MagicMock()
        mock_client.generate_content.return_value = "AI Generated Proposal"
        mock_jules_ai.return_value = mock_client

        proposal = generate_proposal("freelancer", "Test desc", use_ai=True)
        self.assertEqual(proposal, "AI Generated Proposal")
        mock_client.generate_content.assert_called_once()

    @patch('src.proposal_generator.GEMINI_API_KEY', 'fake_key')
    @patch('src.proposal_generator.JulesAI')
    def test_ai_generation_fallback(self, mock_jules_ai):
        mock_client = MagicMock()
        mock_client.generate_content.side_effect = Exception("AI Error")
        mock_jules_ai.return_value = mock_client

        proposal = generate_proposal("freelancer", "Test desc", use_ai=True)
        self.assertIn("### Proposal for Freelancer.com", proposal)

    @patch('src.proposal_generator.GEMINI_API_KEY', None)
    def test_ai_generation_no_key(self):
        proposal = generate_proposal("freelancer", "Test desc", use_ai=True)
        self.assertIn("### Proposal for Freelancer.com", proposal)

    def test_skill_detection(self):
        desc = "I need an Excel VBA expert to automate my sheet"
        skill, strategy = detect_skill(desc)
        self.assertEqual(skill, "Excel VBA")
        self.assertEqual(strategy, "Automation and Macro Optimization")

        desc_seo = "Improve my SEO ranking"
        skill, strategy = detect_skill(desc_seo)
        self.assertEqual(skill, "SEO")
        self.assertEqual(strategy, "Ranking and Keywords Dominance")

        desc_generic = "Help me with something"
        skill, strategy = detect_skill(desc_generic)
        self.assertEqual(skill, "General")

    def test_proposal_customization_with_skill(self):
        desc = "Need help with SQL queries"
        proposal = generate_proposal("freelancer", desc, use_ai=False)
        # Should contain "Core Strategy: Database Optimization..."
        self.assertIn("Core Strategy: Database Optimization", proposal)
        self.assertIn("Skill: SQL", proposal)

if __name__ == "__main__":
    unittest.main()
