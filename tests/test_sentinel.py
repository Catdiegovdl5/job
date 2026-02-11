import sys
from unittest.mock import MagicMock

# Create a mock requests module
mock_requests = MagicMock()
# Define RequestException as a real exception class so it can be caught
class RequestException(Exception):
    pass
mock_requests.exceptions.RequestException = RequestException

# Inject into sys.modules
sys.modules["requests"] = mock_requests

import unittest
from unittest.mock import patch
import os
import json
import sentinel  # Now this imports the mocked requests

class TestSentinel(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test if needed
        mock_requests.post.reset_mock()
        mock_requests.post.side_effect = None
        mock_requests.post.return_value = None # Clear return value too just in case

    @patch('sentinel.GEMINI_API_KEY', 'test_api_key')
    def test_call_jules_success(self):
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

        # Configure the mock requests.post
        mock_requests.post.return_value = mock_response

        result = sentinel.call_jules("Need video", "freelancer")
        self.assertEqual(result, "Generated Proposal")

        # Verify headers
        args, kwargs = mock_requests.post.call_args
        self.assertIn('headers', kwargs)
        self.assertEqual(kwargs['headers']['x-goog-api-key'], 'test_api_key')
        self.assertEqual(kwargs['headers']['Content-Type'], 'application/json')

    def test_call_jules_retry(self):
        # Simulate failure then success
        mock_response_success = MagicMock()
        mock_response_success.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Generated Proposal'}]}}]
        }
        mock_response_success.raise_for_status = MagicMock()

        # Side effect: Raise exception twice, then return success
        mock_requests.post.side_effect = [
            RequestException("Fail 1"),
            RequestException("Fail 2"),
            mock_response_success
        ]

        with patch('sentinel.time.sleep') as mock_sleep: # Speed up test
            result = sentinel.call_jules("Need video", "freelancer")
            self.assertEqual(result, "Generated Proposal")
            self.assertEqual(mock_requests.post.call_count, 3) # Called 3 times

    @patch('sentinel.call_jules')
    def test_fetch_leads(self, mock_call_jules):
        mock_call_jules.return_value = "Mocked Proposal"

        # Ensure the file doesn't exist before test
        if os.path.exists("leads_ready.json"):
            os.remove("leads_ready.json")

        sentinel.fetch_leads()

        self.assertTrue(os.path.exists("leads_ready.json"))
        with open("leads_ready.json", "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 3) # Updated to 3 simulated leads
            self.assertEqual(data[0]['proposal'], "Mocked Proposal")

        # Cleanup
        os.remove("leads_ready.json")

if __name__ == "__main__":
    unittest.main()
