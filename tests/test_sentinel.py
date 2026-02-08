import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
import logging

# Ensure src is in path so sentinel can import from src
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentinel import process_leads, fetch_leads

class TestSentinel(unittest.TestCase):

    def setUp(self):
        # Configure logging to avoid noise during tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        if os.path.exists("leads_ready.json"):
            os.remove("leads_ready.json")

    @patch('sentinel.SIMULATED_LEADS', [{'platform': 'freelancer', 'desc': 'Simulated'}])
    @patch('os.path.exists', return_value=False)
    def test_fetch_leads_simulated(self, mock_exists):
        leads = fetch_leads()
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]['platform'], 'freelancer')

    @patch('builtins.open', new_callable=mock_open, read_data='[{"platform": "upwork", "desc": "File Lead"}]')
    @patch('os.path.exists')
    def test_fetch_leads_from_file(self, mock_exists, mock_file):
        mock_exists.return_value = True
        leads = fetch_leads()
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]['platform'], 'upwork')

    @patch('sentinel.generate_proposal')
    @patch('sentinel.fetch_leads')
    def test_process_leads(self, mock_fetch, mock_generate):
        mock_fetch.return_value = [{'platform': 'freelancer', 'desc': 'Test Desc'}]
        mock_generate.return_value = "Generated Proposal"

        process_leads()

        # Check if leads_ready.json was created
        self.assertTrue(os.path.exists("leads_ready.json"))
        with open("leads_ready.json", "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['proposal'], "Generated Proposal")

        mock_generate.assert_called_with('freelancer', 'Test Desc', None, use_ai=True)

if __name__ == "__main__":
    unittest.main()
