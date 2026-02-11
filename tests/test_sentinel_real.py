import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import io
import http.server

# Mock dependencies globally before importing sentinel_real
mock_requests = MagicMock()
mock_telebot = MagicMock()
mock_groq = MagicMock()
mock_freelancersdk = MagicMock()

sys.modules['requests'] = mock_requests
sys.modules['telebot'] = mock_telebot
sys.modules['telebot.types'] = MagicMock()
sys.modules['groq'] = mock_groq
sys.modules['freelancersdk.session'] = mock_freelancersdk
sys.modules['freelancersdk.resources.projects.projects'] = MagicMock()
sys.modules['freelancersdk.resources.projects.helpers'] = MagicMock()

# Set environment variables for import
os.environ['TG_TOKEN'] = 'test_token'
os.environ['GROQ_API_KEY'] = 'test_key'
os.environ['API_SECRET'] = '1234'

import sentinel_real
from sentinel_real import gerar_proposta_groq, save_memory, scan_radar, callback_handler, APIHandler

class TestSentinelReal(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test
        mock_groq.reset_mock()
        mock_requests.reset_mock()
        mock_telebot.reset_mock()

        # Reset memory for testing
        sentinel_real.memory.clear()
        sentinel_real.memory["current_mission"] = "python automation scraping"

    def test_gerar_proposta_groq_sanitization(self):
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Subject: Proposal\n**Hook:** I saw your project. Dear Client, I'm excited to bid."
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq.Groq.return_value = mock_client

        with patch('sentinel_real.GROQ_KEY', 'test_key'):
             result = gerar_proposta_groq("Test Project", "Description")

        self.assertNotIn("Subject:", result)
        self.assertNotIn("**Hook:**", result)
        self.assertNotIn("Dear Client,", result)
        self.assertNotIn("I'm excited to bid", result)
        self.assertIn("I analyzed your requirements", result)

    def test_callback_handler_mission_switch(self):
        mock_call = MagicMock()
        mock_call.data = "set_web"
        mock_call.message.chat.id = 123
        mock_call.id = "456"

        mock_bot = MagicMock()
        sentinel_real.bot = mock_bot

        callback_handler(mock_call)

        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")
        mock_bot.answer_callback_query.assert_called_with("456", "Modo: 🌐 Web Dev")

    def test_callback_handler_split_limit(self):
        mock_call = MagicMock()
        mock_call.data = "approve_project_123_abc"
        mock_call.message.chat.id = 123
        mock_call.id = "456"

        mock_bot = MagicMock()
        sentinel_real.bot = mock_bot

        sentinel_real.memory["project_123_abc"] = {'alert_id': 1, 'prop_id': 2}

        callback_handler(mock_call)

        mock_bot.answer_callback_query.assert_called_with("456", "✅ Aprovado!")
        args, kwargs = mock_bot.edit_message_text.call_args
        self.assertIn("project_123_abc", args[0])

    def test_api_handler_get(self):
        handler = APIHandler.__new__(APIHandler)
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.end_headers = MagicMock()

        handler.do_GET()

        handler.send_response.assert_called_with(200)
        self.assertIn(b"ONLINE - API READY", handler.wfile.getvalue())

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
        self.assertIn(b"success", handler.wfile.getvalue())
        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")

    def test_api_handler_post_status(self):
        handler = APIHandler.__new__(APIHandler)
        handler.headers = {'X-Api-Key': '1234'}
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.send_headers = MagicMock()
        handler.end_headers = MagicMock()
        handler.path = "/api/status"

        handler.do_POST()

        handler.send_response.assert_called_with(200)
        # Verify end_headers() is called, NOT send_headers()
        handler.end_headers.assert_called()
        handler.send_headers.assert_not_called()

        response = json.loads(handler.wfile.getvalue().decode())
        self.assertTrue(response["online"])
        self.assertIn("current_mission", response)

    def test_api_handler_post_invalid_auth(self):
        handler = APIHandler.__new__(APIHandler)
        handler.headers = {'X-Api-Key': 'wrong_key'}
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.end_headers = MagicMock()

        handler.do_POST()

        handler.send_response.assert_called_with(403)

if __name__ == "__main__":
    unittest.main()
