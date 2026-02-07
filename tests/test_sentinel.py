import unittest
from unittest.mock import patch, MagicMock
import os
import json
import requests
from src.config import ARSENAL
from sentinel import call_jules, fetch_leads

class TestSentinel(unittest.TestCase):

    def setUp(self):
        # Clean up any existing leads file
        if os.path.exists("leads_ready.json"):
            os.remove("leads_ready.json")

    def tearDown(self):
        if os.path.exists("leads_ready.json"):
            os.remove("leads_ready.json")

    @patch('requests.post')
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
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

        # Verify ARSENAL is in the prompt
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        prompt_text = payload['contents'][0]['parts'][0]['text']

        for key, value in ARSENAL.items():
            self.assertIn(value, prompt_text)

    @patch('requests.post')
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    def test_call_jules_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        result = call_jules("Need video", "freelancer")
        self.assertIn("Request timed out", result)

    @patch('sentinel.call_jules')
    def test_fetch_leads(self, mock_call_jules):
        mock_call_jules.return_value = "Mocked Proposal"

        fetch_leads()

        self.assertTrue(os.path.exists("leads_ready.json"))
        with open("leads_ready.json", "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['proposal'], "Mocked Proposal")

if __name__ == "__main__":
    unittest.main()
