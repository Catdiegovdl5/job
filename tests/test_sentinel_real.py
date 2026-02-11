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
from sentinel_real import gerar_proposta_groq, save_memory

class TestSentinelReal(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test
        mock_groq.reset_mock()
        mock_requests.reset_mock()

    def test_gerar_proposta_groq_success(self):
        # Mock Groq client
        mock_client = MagicMock()
        mock_completion = MagicMock()
        # Mocking a response that might contain things to filter
        mock_completion.choices[0].message.content = "Subject: Proposal\nI'm Jules. Here is the hook. [Client Name] should know this."
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq.Groq.return_value = mock_client

        # We don't need to patch GROQ_KEY because it was set at import time via os.environ
        # But to be safe if tests run in different order or reloading happens:
        with patch('sentinel_real.GROQ_KEY', 'test_key'):
             result = gerar_proposta_groq("Test Project", "Description")

        # Verify sanitization logic
        self.assertNotIn("Subject:", result)
        self.assertNotIn("Jules", result)
        self.assertNotIn("[Client Name]", result)
        self.assertIn("Diego", result) # Replaced Jules

    def test_save_memory(self):
        data = {"test": "data"}
        # Ensure file doesn't exist
        if os.path.exists("memory.json"):
            os.remove("memory.json")

        save_memory(data)

        self.assertTrue(os.path.exists("memory.json"))
        with open("memory.json", "r") as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data, data)

        # Cleanup
        os.remove("memory.json")

if __name__ == "__main__":
    unittest.main()
