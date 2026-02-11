import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json
import io
import threading
import importlib

# Mock dependencies globally before importing sentinel_real
mock_requests = MagicMock()
mock_telebot = MagicMock()
mock_freelancersdk = MagicMock()

# Configure TeleBot mocks to handle decorators correctly
def pass_through_decorator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

# Configure the bot instance mock that will be returned by TeleBot()
mock_bot_instance = MagicMock()
mock_bot_instance.callback_query_handler.side_effect = pass_through_decorator
mock_bot_instance.message_handler.side_effect = pass_through_decorator

mock_telebot.TeleBot.return_value = mock_bot_instance

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
# Force reload to ensure bot uses the configured mock with pass-through decorators
importlib.reload(sentinel_real)
from sentinel_real import gerar_proposta_diego, save_memory, callback_handler, APIHandler

class TestSentinelReal(unittest.TestCase):

    def setUp(self):
        mock_requests.reset_mock()
        mock_telebot.reset_mock()
        mock_bot_instance.reset_mock()
        # Reset memory state
        with sentinel_real.memory_lock:
            sentinel_real.memory.clear()
            sentinel_real.memory["current_mission"] = "python automation scraping"

    @patch("builtins.open", new_callable=mock_open)
    def test_gerar_proposta_diego_success(self, mock_file):
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
        self.assertNotIn("**Hook:**", result)
        self.assertNotIn("Dear Client,", result)
        self.assertIn("I analyzed your requirements", result)
        self.assertIsInstance(result, str)

    @patch("sentinel_real.logger")
    @patch("builtins.open", new_callable=mock_open)
    def test_callback_handler_mission_switch(self, mock_file, mock_logger):
        mock_call = MagicMock()
        mock_call.data = "set_web"
        mock_call.message.chat.id = 123
        mock_call.id = "456"

        callback_handler(mock_call)

        if mock_logger.error.called:
            self.fail(f"Logger error called: {mock_logger.error.call_args}")

        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")
        mock_bot_instance.answer_callback_query.assert_called_with("456", "Modo: 🌐 Web Dev")
        mock_file.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    def test_api_handler_post_set_mode(self, mock_file):
        handler = APIHandler.__new__(APIHandler)
        # Corrected Content-Length to 15 as requested
        handler.headers = {'X-Api-Key': '1234', 'Content-Length': '15'}

        handler.rfile = io.BytesIO(b'{"mode": "web"}')
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.end_headers = MagicMock()
        handler.path = "/api/set_mode"

        handler.do_POST()

        handler.send_response.assert_called_with(200)
        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")

        # Robust Validation
        self.assertEqual(mock_bot_instance.send_message.call_count, 2)
        args, _ = mock_bot_instance.send_message.call_args_list[1]
        self.assertIn("[COMANDO OPAL]", args[1])

if __name__ == "__main__":
    unittest.main()
