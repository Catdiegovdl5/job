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

import sentinel_real
from sentinel_real import gerar_proposta_diego, save_memory, callback_handler, APIHandler

class TestSentinelReal(unittest.TestCase):

    def setUp(self):
        mock_requests.reset_mock()
        mock_telebot.reset_mock()
        sentinel_real.memory.clear()
        sentinel_real.memory["current_mission"] = "python automation scraping"

    def test_gerar_proposta_diego_success(self):
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

        self.assertNotIn("Subject:", result)
        self.assertNotIn("Dear Client,", result)
        self.assertIn("I analyzed your requirements", result)
        self.assertIsInstance(result, str)

    def test_callback_handler_mission_switch(self):
        mock_call = MagicMock()
        mock_call.data = "set_web"
        mock_call.message.chat.id = 123
        mock_call.id = "456"

        mock_bot = MagicMock()

        # Patch sentinel_real.bot.
        # Ensure we patch it in the right place so the function uses it.
        sentinel_real.bot = mock_bot

        callback_handler(mock_call)

        # We need to access memory from the module
        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")
        mock_bot.answer_callback_query.assert_called_with("456", "Modo: 🌐 Web Dev")

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

        args, _ = mock_bot.send_message.call_args_list[1]
        self.assertIn("[COMANDO OPAL]", args[1])

if __name__ == "__main__":
    unittest.main()
