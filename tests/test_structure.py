import sys
import os
import unittest

# Add root to path to allow importing src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.scout import Scout
from src.ai_client import AIClient
from src.telegram_bot import TelegramCommander

class TestStructure(unittest.TestCase):
    def test_scout_init(self):
        try:
            s = Scout()
            self.assertIsNotNone(s)
        except Exception as e:
            self.fail(f"Scout init failed: {e}")

    def test_ai_client_init(self):
        try:
            a = AIClient()
            self.assertIsNotNone(a)
        except Exception as e:
            self.fail(f"AIClient init failed: {e}")

    def test_telegram_commander_init(self):
        try:
            t = TelegramCommander()
            self.assertIsNotNone(t)
        except Exception as e:
            self.fail(f"TelegramCommander init failed: {e}")

if __name__ == '__main__':
    unittest.main()
