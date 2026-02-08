import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add root to sys.path so we can import src as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.proposal_generator import generate_proposal

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
        # Only mock_jules_ai is passed because GEMINI_API_KEY uses 'new' argument (implicit position)
        # Wait, order of decorators matters.
        # Top decorator is last argument?
        # @patch('A') -> arg1
        # @patch('B') -> arg2
        # def test(self, arg1, arg2)
        # Here:
        # @patch('GEMINI_API_KEY', 'fake_key') -> Not passed
        # @patch('JulesAI') -> Passed as mock_jules_ai
        # So signature is correct: (self, mock_jules_ai)

        mock_client = MagicMock()
        mock_client.generate_content.return_value = "AI Generated Proposal"
        mock_jules_ai.return_value = mock_client

        proposal = generate_proposal("freelancer", "Test desc", use_ai=True)
        self.assertEqual(proposal, "AI Generated Proposal")
        # Check if generate_content was called
        mock_client.generate_content.assert_called_once()

    @patch('src.proposal_generator.GEMINI_API_KEY', 'fake_key')
    @patch('src.proposal_generator.JulesAI')
    def test_ai_generation_fallback(self, mock_jules_ai):
        mock_client = MagicMock()
        mock_client.generate_content.side_effect = Exception("AI Error")
        mock_jules_ai.return_value = mock_client

        # Should fallback to template which contains "### Proposal for Freelancer.com"
        proposal = generate_proposal("freelancer", "Test desc", use_ai=True)
        self.assertIn("### Proposal for Freelancer.com", proposal)

    @patch('src.proposal_generator.GEMINI_API_KEY', None)
    def test_ai_generation_no_key(self):
        # Should fallback to template immediately
        proposal = generate_proposal("freelancer", "Test desc", use_ai=True)
        self.assertIn("### Proposal for Freelancer.com", proposal)

if __name__ == "__main__":
    unittest.main()
