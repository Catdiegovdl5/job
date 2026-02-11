import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Mock requests module globally before importing sentinel_real
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from sentinel_real import gerar_proposta_groq, fetch_leads, save_memory

class TestSentinelReal(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test
        mock_requests.reset_mock()

    def test_gerar_proposta_groq_success(self):
        # Configure the mock response with "Jules" and "Dear Client" to test sanitization
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': "Dear Client,\nI'm excited to bid on this project for [X]. Signed, Jules"}]
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests.post.return_value = mock_response

        result = gerar_proposta_groq("Need video", "freelancer")

        # Verify sanitization logic
        self.assertNotIn("Dear Client,", result)
        self.assertNotIn("I'm excited to bid", result)
        self.assertIn("I analyzed your requirements", result)
        self.assertIn("Signed, Diego", result)
        self.assertIn("negotiable", result)

    @patch('sentinel_real.gerar_proposta_groq')
    def test_fetch_leads(self, mock_gerar_proposta_groq):
        mock_gerar_proposta_groq.return_value = "Mocked Proposal"

        # Ensure file doesn't exist
        if os.path.exists("leads_ready.json"):
            os.remove("leads_ready.json")

        fetch_leads()

        self.assertTrue(os.path.exists("leads_ready.json"))
        with open("leads_ready.json", "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['proposal'], "Mocked Proposal")

        # Cleanup
        os.remove("leads_ready.json")

    def test_save_memory(self):
        data = [{"test": "data"}]
        # Ensure file doesn't exist
        if os.path.exists("leads_ready.json"):
            os.remove("leads_ready.json")

        save_memory(data)

        self.assertTrue(os.path.exists("leads_ready.json"))
        with open("leads_ready.json", "r") as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data, data)

        # Cleanup
        os.remove("leads_ready.json")

if __name__ == "__main__":
    unittest.main()
