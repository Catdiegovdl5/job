import unittest
from unittest.mock import patch, MagicMock
from src.worker import ServiceAgent

class TestServiceAgent(unittest.TestCase):

    @patch('src.worker.JulesAI')
    @patch('src.worker.GEMINI_API_KEY', 'fake_key')
    def test_execute_task_excel(self, mock_ai_class):
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = "VBA Code Block"
        mock_ai_class.return_value = mock_instance

        agent = ServiceAgent()
        result = agent.execute_task("Excel/SQL", "Create a macro")

        self.assertEqual(result, "VBA Code Block")
        mock_instance.generate_content.assert_called_once()
        args, _ = mock_instance.generate_content.call_args
        self.assertIn("Automation Engineer", args[0])

    @patch('src.worker.JulesAI')
    @patch('src.worker.GEMINI_API_KEY', 'fake_key')
    def test_execute_task_seo(self, mock_ai_class):
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = "SEO Article"
        mock_ai_class.return_value = mock_instance

        agent = ServiceAgent()
        result = agent.execute_task("SEO/Writing", "Write about AI")

        self.assertEqual(result, "SEO Article")
        args, _ = mock_instance.generate_content.call_args
        self.assertIn("SEO Specialist", args[0])

if __name__ == "__main__":
    unittest.main()
