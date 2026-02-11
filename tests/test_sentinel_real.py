import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

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

import sentinel_real
from sentinel_real import gerar_proposta_groq, save_memory, scan_radar, callback_handler

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
        # Test specific replacements requested
        mock_completion.choices[0].message.content = "Dear Client,\nI'm excited to bid on your project. Signed, Jules"
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq.Groq.return_value = mock_client

        with patch('sentinel_real.GROQ_KEY', 'test_key'):
             result = gerar_proposta_groq("Test Project", "Description")

        # Verify sanitization logic restored
        self.assertNotIn("Dear Client,", result)
        self.assertNotIn("Jules", result)
        self.assertNotIn("I'm excited to bid", result)

        self.assertIn("Diego", result)
        self.assertIn("I analyzed your requirements", result)

    def test_callback_handler_mission_switch(self):
        mock_call = MagicMock()
        mock_call.data = "set_web"
        mock_call.message.chat.id = 123
        mock_call.id = "456"

        mock_bot = MagicMock()
        sentinel_real.bot = mock_bot

        callback_handler(mock_call)

        # The previous failure was likely due to memory variable reference.
        # sentinel_real.memory is the reference we are checking.
        # Ensure that callback_handler modifies the same object.
        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")

        mock_bot.answer_callback_query.assert_called_with("456", "Modo: 🌐 Web Dev")
        mock_bot.send_message.assert_called()

    def test_callback_handler_split_limit(self):
        # Test the split logic with underscores in ID
        mock_call = MagicMock()
        mock_call.data = "approve_project_123_abc"
        mock_call.message.chat.id = 123
        mock_call.id = "456"

        mock_bot = MagicMock()
        sentinel_real.bot = mock_bot

        # Mock memory to simulate the project being monitored
        sentinel_real.memory["project_123_abc"] = {'alert_id': 1, 'prop_id': 2}

        callback_handler(mock_call)

        # The previous failure "Actual: not called" suggests that the handler might have returned early
        # or failed. If split failed, it would raise exception and be caught (silent fail due to try-except pass).
        # With split("_", 1), it should work.

        # Check if answer_callback_query was called
        # If not, check if we entered the block.
        # call.data contains underscore, so "_" in call.data is True.

        mock_bot.answer_callback_query.assert_called_with("456", "✅ Aprovado!")

        # Check edit message argument
        args, kwargs = mock_bot.edit_message_text.call_args
        self.assertIn("project_123_abc", args[0])

if __name__ == "__main__":
    unittest.main()
