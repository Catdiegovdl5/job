import unittest
from unittest.mock import patch, MagicMock
import os

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

    def test_escape_markdown(self):
        raw = "Hello_World *Test* [Link]"
        # sentinel_real escapes _ * [ and backtick.
        # We test _ * and [ here.
        escaped = sentinel_real.escape_markdown(raw)
        # Expected: backslash before special chars
        expected = "Hello\\_World \\*Test\\* \\[Link]"
        self.assertEqual(escaped, expected)

    @patch('sentinel_real.logger')
    def test_check_env_var_missing(self, mock_logger):
        with patch.dict(os.environ, {}, clear=True):
             val = sentinel_real.check_env_var("MISSING_VAR_TEST")
             self.assertIsNone(val)
             mock_logger.error.assert_called_with("❌ ERRO CRITICO: Variável MISSING_VAR_TEST não encontrada no .env ou sistema")

if __name__ == "__main__":
    unittest.main()
