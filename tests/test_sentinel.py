import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Mock requests module globally before importing sentinel
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from sentinel import gerar_proposta_groq, fetch_leads, save_memory

class TestSentinel(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test
        mock_requests.reset_mock()

    def test_gerar_proposta_groq_success(self):
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': 'Diego Proposal'}]
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests.post.return_value = mock_response

        result = gerar_proposta_groq("Need video", "freelancer")
        self.assertEqual(result, "Diego Proposal")

    @patch('sentinel.gerar_proposta_groq')
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
