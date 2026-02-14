import unittest
from unittest.mock import patch, mock_open, MagicMock
import status_jules
import logging

class TestStatusJules(unittest.TestCase):

    @patch('status_jules.logging')
    @patch('builtins.open', new_callable=mock_open, read_data="https://vm.tiktok.com/ZM8abc123/\nhttps://vt.tiktok.com/ZSxyz789/")
    @patch('os.listdir')
    @patch('os.path.exists')
    def test_check_status(self, mock_exists, mock_listdir, mock_file, mock_logging):
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.side_effect = [
            ['dir1', 'dir2'], # PASTA_FONTE
            ['dir3'],         # PASTA_CERTO
            []                # PASTA_LIXO
        ]

        # We also need to mock os.path.isdir inside the listdir comprehension
        with patch('os.path.isdir', return_value=True):
            status_jules.check_status()

        # Verify logging calls
        # 2 links in mock_open data
        # 2 pending (dir1, dir2)
        # 1 approved (dir3)
        # 0 discarded

        # Check for specific log messages
        calls = [call[0][0] for call in mock_logging.info.call_args_list]
        self.assertIn("📥 Links detectados na conversa: 2", calls)
        self.assertIn("⏳ Itens aguardando auditoria: 2", calls)
        self.assertIn("✅ Músicas aprovadas (CERTO): 1", calls)
        self.assertIn("❌ Músicas descartadas (LIXO): 0", calls)

if __name__ == '__main__':
    unittest.main()
