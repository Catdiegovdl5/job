import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import io
import threading

# Mock dependencies globally before importing sentinel_real
mock_requests = MagicMock()
mock_telebot = MagicMock()
mock_freelancersdk = MagicMock()

sys.modules['requests'] = mock_requests
sys.modules['telebot'] = mock_telebot
sys.modules['telebot.types'] = MagicMock()
sys.modules['freelancersdk.session'] = mock_freelancersdk
sys.modules['freelancersdk.resources.projects.projects'] = MagicMock()
sys.modules['freelancersdk.resources.projects.helpers'] = MagicMock()

# Set environment variables for import
os.environ['TG_TOKEN'] = 'test_token'
os.environ['GEMINI_API_KEY'] = 'test_gemini_key'
os.environ['API_SECRET'] = '1234'

# IMPORTANTE: Importando do nome correto do arquivo e a função nova
import sentinel_real
from sentinel_real import gerar_proposta_diego, save_memory, callback_handler, APIHandler

class TestSentinelReal(unittest.TestCase):

    def setUp(self):
        mock_requests.reset_mock()
        mock_telebot.reset_mock()
        sentinel_real.memory.clear()
        sentinel_real.memory["current_mission"] = "python automation scraping"

    def test_gerar_proposta_diego_success(self):
        # Mock do Gemini (Requests)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': "Subject: Proposal\n**Hook:** I saw your project. Dear Client, I'm excited to bid."}]
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests.post.return_value = mock_response

        with patch('sentinel_real.GEMINI_API_KEY', 'test_key'):
             result = gerar_proposta_diego("Test Project", "Description")

        # Verificações de higienização (Diego Mode)
        self.assertNotIn("Subject:", result)
        self.assertNotIn("Dear Client,", result)
        self.assertIn("I analyzed your requirements", result)
        # O código original não adiciona "Signed, Diego" explicitamente no retorno,
        # ele apenas substitui "Jules" por "Diego" se aparecer.
        # Então verificamos se o texto foi processado.
        self.assertIsInstance(result, str)

    def test_api_handler_post_set_mode(self):
        handler = APIHandler.__new__(APIHandler)
        handler.headers = {'X-Api-Key': '1234', 'Content-Length': '16'}

        handler.rfile = io.BytesIO(b'{"mode": "web"}')
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.end_headers = MagicMock()
        handler.path = "/api/set_mode"

        mock_bot = MagicMock()
        sentinel_real.bot = mock_bot

        handler.do_POST()

        handler.send_response.assert_called_with(200)
        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")

if __name__ == "__main__":
    unittest.main()
