import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# We need to mock os.environ.get BEFORE importing sentinel_real
# because it runs top-level code that calls check_env_var
mock_env = {
    "TG_TOKEN": "1234:testtoken",
    "TG_CHAT_ID": "12345",
    "FLN_OAUTH_TOKEN": "fln_test_token",
    "GROQ_API_KEY": "gsk_test_key"
}

with patch.dict(os.environ, mock_env):
    import sentinel_real

class TestDiegoElite(unittest.TestCase):
    def test_memory_load(self):
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

    @patch('sentinel_real.logger')
    def test_check_env_var_missing(self, mock_logger):
        with patch.dict(os.environ, {}, clear=True):
             val = sentinel_real.check_env_var("MISSING_VAR")
             self.assertIsNone(val)
             mock_logger.error.assert_called_with("❌ ERRO: Variável MISSING_VAR não encontrada no .env")

if __name__ == "__main__":
    unittest.main()
