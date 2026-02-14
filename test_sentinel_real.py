import unittest
from unittest.mock import patch, MagicMock
import os
import sentinel_real

class TestDiegoElite(unittest.TestCase):
    def test_memory_load(self):
        mem = sentinel_real.load_memory()
        self.assertIn("current_mission", mem)

    @patch('requests.post')
    def test_gemini_diego_logic(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'candidates': [{'content': {'parts': [{'text': 'Diego Proposal'}]}}]}
        mock_post.return_value = mock_response
        res = sentinel_real.gerar_proposta_diego("Test", "Desc")
        self.assertIn("Diego", res)

if __name__ == "__main__":
    unittest.main()
