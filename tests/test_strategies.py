import unittest
import sys
import os

# Add src to sys.path to ensure we can import the module even if run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from strategies import ProposalStrategy

class TestProposalStrategy(unittest.TestCase):

    def test_freelancer_prompt(self):
        prompt = ProposalStrategy.get_prompt("freelancer", "Test Description")
        self.assertIn("Plataforma: Freelancer.com", prompt)
        self.assertIn("Idioma: Inglês", prompt)
        self.assertIn("Velocidade e Resposta Técnica", prompt)
        self.assertIn("Pipeline Veo 3", prompt)

    def test_99freelas_prompt(self):
        prompt = ProposalStrategy.get_prompt("99freelas", "Test Description")
        self.assertIn("Plataforma: 99Freelas", prompt)
        self.assertIn("Idioma: Português", prompt)
        self.assertIn("ROI e Consultoria", prompt)
        self.assertIn("Projeto Piloto", prompt)

    def test_upwork_prompt(self):
        prompt = ProposalStrategy.get_prompt("upwork", "Test Description")
        self.assertIn("Plataforma: Upwork", prompt)
        self.assertIn("Idioma: Inglês", prompt)
        self.assertIn("Senioridade e Estudos de Caso", prompt)
        # Check specific Upwork keywords
        self.assertIn("High-Fidelity", prompt)

    def test_generic_prompt(self):
        prompt = ProposalStrategy.get_prompt("unknown", "Test Description")
        self.assertIn("Plataforma: Genérica", prompt)
        self.assertIn("Melhor solução técnica possível", prompt)

if __name__ == '__main__':
    unittest.main()
