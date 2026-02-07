import unittest
import sys
import os

# Add src to sys.path in a portable way
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proposal_generator import generate_proposal

class TestProposalGenerator(unittest.TestCase):
    def test_freelancer_proposal(self):
        desc = "Need a video for my website"
        proposal = generate_proposal("freelancer", desc)
        self.assertIn("### Proposal for Freelancer.com", proposal)
        self.assertIn("Pipeline Veo 3", proposal)
        self.assertIn("Test Keywords", proposal)
        self.assertIn("Language: English", proposal)

    def test_99freelas_proposal(self):
        desc = "Preciso de tráfego pago"
        proposal = generate_proposal("99freelas", desc)
        self.assertIn("### Proposta para 99Freelas", proposal)
        self.assertIn("Projeto Piloto", proposal)
        self.assertIn("Idioma: Português", proposal)

    def test_upwork_proposal(self):
        desc = "Looking for an SEO expert"
        questions = ["How do you handle SEO?"]
        proposal = generate_proposal("upwork", desc, questions)
        self.assertIn("### Proposal for Upwork", proposal)
        self.assertIn("Screening Questions", proposal)
        self.assertIn("GEO (Generative Engine Optimization)", proposal)

    def test_invalid_platform(self):
        proposal = generate_proposal("invalid", "test")
        self.assertIn("Error: Unsupported platform", proposal)

if __name__ == '__main__':
    unittest.main()
