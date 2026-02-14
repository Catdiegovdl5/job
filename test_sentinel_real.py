import unittest
from unittest.mock import patch, MagicMock
import os
import sentinel_real

class TestDiegoElite(unittest.TestCase):
    def test_memory_load(self):
        # We need to make sure MEMORY_FILE does not exist or mock it
        with patch("os.path.exists", return_value=False):
            mem = sentinel_real.load_memory()
            self.assertIn("current_mission", mem)

    @patch('sentinel_real.client_groq')
    def test_groq_diego_logic(self, mock_client):
        # Setup mock response
        mock_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        mock_client.chat.completions.create.return_value = mock_completion
        mock_completion.choices = [mock_choice]
        mock_choice.message = mock_message
        mock_message.content = "Diego Proposal"

        res = sentinel_real.gerar_proposta_diego("Test", "Desc")
        self.assertIn("Diego", res)

    def test_gerar_proposta_no_client(self):
        # Temporarily unset client_groq
        original_client = sentinel_real.client_groq
        sentinel_real.client_groq = None
        res = sentinel_real.gerar_proposta_diego("Test", "Desc")
        self.assertIn("Erro: Groq não configurado", res)
        sentinel_real.client_groq = original_client

if __name__ == "__main__":
    unittest.main()
