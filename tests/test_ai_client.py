import unittest
from unittest.mock import patch, MagicMock
from src.ai_client import JulesAI

class TestJulesAI(unittest.TestCase):

    def setUp(self):
        self.client = JulesAI(api_key="test_key")

    @patch('requests.post')
    def test_generate_content_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Generated Content'}]}}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        content = self.client.generate_content("Test Prompt")
        self.assertEqual(content, "Generated Content")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_generate_content_retry_success(self, mock_post):
        # First attempt fails, second succeeds
        mock_response_success = MagicMock()
        mock_response_success.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'Generated Content'}]}}]
        }
        mock_response_success.raise_for_status = MagicMock()

        import requests
        mock_post.side_effect = [requests.exceptions.RequestException("Network Error"), mock_response_success]

        content = self.client.generate_content("Test Prompt", retries=2, backoff_factor=0.01)
        self.assertEqual(content, "Generated Content")
        self.assertEqual(mock_post.call_count, 2)

    @patch('requests.post')
    def test_generate_content_failure(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Persistent Error")

        content = self.client.generate_content("Test Prompt", retries=2, backoff_factor=0.01)
        self.assertTrue("Error calling Gemini API" in content)
        self.assertEqual(mock_post.call_count, 2)

    def test_missing_api_key(self):
        client = JulesAI(api_key=None)
        # Mock global config if needed, or rely on it being None in test env if not set
        # But here we explicitly pass None to constructor, so it might take from config.
        # Let's ensure config is None or we force it.
        # Actually, JulesAI constructor takes api_key or GEMINI_API_KEY.
        # If GEMINI_API_KEY is in env, it might be set.
        # We can patch the config import or just check behavior.

        # Let's try to instantiate with None and ensure it raises ValueError
        # We need to patch src.ai_client.GEMINI_API_KEY to be None
        with patch('src.ai_client.GEMINI_API_KEY', None):
            client = JulesAI(api_key=None)
            with self.assertRaises(ValueError):
                client.generate_content("Prompt")

if __name__ == "__main__":
    unittest.main()
