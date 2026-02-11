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

    def test_gerar_proposta_groq_success(self):
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Subject: Proposal\n**Hook:** I saw your project. [Client Name]\n## Plan\n1. Phase 1\n| Phase | Action |\n|---|---|"
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq.Groq.return_value = mock_client

        with patch('sentinel_real.GROQ_KEY', 'test_key'):
             result = gerar_proposta_groq("Test Project", "Description")

        self.assertNotIn("Subject:", result)
        self.assertNotIn("**Hook:**", result)
        self.assertNotIn("## Plan", result)
        self.assertNotIn("| Phase | Action |", result)
        self.assertNotIn("[Client Name]", result)

    def test_callback_handler_mission_switch(self):
        mock_call = MagicMock()
        mock_call.data = "set_web"
        mock_call.message.chat.id = 123
        mock_call.id = "456"

        mock_bot = MagicMock()

        # Patch sentinel_real.bot. Because callback_handler accesses 'bot' from the global namespace
        # we need to make sure we patch it there.
        # ALSO,  is a global variable.  modifies .
        #  is imported from  as .

        sentinel_real.bot = mock_bot

        # Call the function
        callback_handler(mock_call)

        # Debugging: check if the handler actually ran the if block
        # The logic is: if call.data.startswith("set_"): ...
        # My call.data is "set_web"

        # Verify memory updated
        # The issue might be that  variable in callback_handler is not the same as
        # because  is defined at module level.
        # But  uses  from global scope, which IS .

        self.assertEqual(sentinel_real.memory["current_mission"], "website react wordpress nodejs")

        # Verify user notified
        mock_bot.answer_callback_query.assert_called_with("456", "Modo: 🌐 Web Dev")
        mock_bot.send_message.assert_called()

    def test_save_memory(self):
        data = {"test": "data"}
        if os.path.exists("memory.json"):
            os.remove("memory.json")

        save_memory(data)

        self.assertTrue(os.path.exists("memory.json"))
        with open("memory.json", "r") as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data, data)

        os.remove("memory.json")

if __name__ == "__main__":
    unittest.main()
