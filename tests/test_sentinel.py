import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

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

# Import from sentinel_real as requested
import sentinel_real
from sentinel_real import gerar_proposta_diego, save_memory

class TestSentinel(unittest.TestCase):

    def setUp(self):
        mock_requests.reset_mock()
        mock_telebot.reset_mock()
        sentinel_real.memory.clear()
        sentinel_real.memory["current_mission"] = "python automation scraping"

    def test_gerar_proposta_diego_success(self):
        # Mock Gemini response (Requests)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': "Subject: Proposal\n**Hook:** I saw your project. Dear Client, I'm excited to bid. Signed, Jules"}]
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests.post.return_value = mock_response

        with patch('sentinel_real.GEMINI_API_KEY', 'test_key'):
             result = gerar_proposta_diego("Test Project", "Description")

        # Verify sanitization (Diego Protocol)
        self.assertNotIn("Subject:", result)
        self.assertNotIn("Dear Client,", result)
        self.assertNotIn("Jules", result)

        self.assertIn("Diego", result) # Should replace Jules
        self.assertIn("I analyzed your requirements", result) # Should replace 'excited to bid'

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
