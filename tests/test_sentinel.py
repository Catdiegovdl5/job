import unittest
import sys
from unittest.mock import MagicMock, patch

# Mock requests before importing sentinel
mock_requests = MagicMock()
mock_requests.exceptions = MagicMock()
mock_requests.exceptions.RequestException = Exception
sys.modules["requests"] = mock_requests

import os
import json
from sentinel import call_jules, fetch_leads

class TestSentinel(unittest.TestCase):

    @patch('requests.post')
    def test_call_jules_success(self, mock_post):
        # Mocking the Gemini API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [
                {
                    'content': {
                        'parts': [{'text': 'Generated Proposal'}]
                    }
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = call_jules("Need video", "freelancer")
        self.assertEqual(result, "Generated Proposal")

    @patch('sentinel.call_jules')
    def test_fetch_leads(self, mock_call_jules):
        mock_call_jules.return_value = "Mocked Proposal"

        # Ensure the file doesn't exist before test
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

if __name__ == "__main__":
    unittest.main()
