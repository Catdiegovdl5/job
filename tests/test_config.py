import unittest
from src.config import ARSENAL

class TestConfig(unittest.TestCase):
    def test_arsenal_structure(self):
        self.assertIn("video", ARSENAL)
        self.assertIn("traffic", ARSENAL)
        self.assertIn("seo", ARSENAL)
        self.assertIn("content", ARSENAL)
        self.assertIsInstance(ARSENAL["video"], str)

if __name__ == '__main__':
    unittest.main()
