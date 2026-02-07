import os
import time
import requests

class TelegramCommander:
    _instance = None
    _last_sent = {}
    _hunting_start_time = 0

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TelegramCommander, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.is_hunting = False
            self.token = os.getenv("TELEGRAM_TOKEN")
            self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
            self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def _send_request(self, text):
        if not self.token or not self.chat_id:
            print(f"[TELEGRAM MOCK] {text}")
            return

        try:
            payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}
            requests.post(self.api_url, json=payload, timeout=5)
        except Exception as e:
            print(f"[TELEGRAM ERROR] Failed to send: {e}")

    def notify_start_hunting(self):
        now = time.time()
        # Cooldown: Don't spam "Start Hunting" if sent recently (e.g., within 1 hour)
        if not self.is_hunting or (now - self._hunting_start_time > 3600):
            self._send_request("Sniper Scout: *Pronto para caçar!* 🦅")
            self.is_hunting = True
            self._hunting_start_time = now

    def notify_stop_hunting(self):
        if self.is_hunting:
            self._send_request("Sniper Scout: *Pausando a caça.* 💤")
            self.is_hunting = False

    def notify_high_score(self, proposal_title, score, url):
        # Anti-Spam: Don't send duplicate alerts for the same job in a short window
        key = f"high_score_{proposal_title}"
        last_time = self._last_sent.get(key, 0)
        if time.time() - last_time < 3600: # 1 hour cooldown per job
            return

        if int(score) > 80:
             msg = f"🎯 *ALVO ENCONTRADO!*\n\n*Title:* {proposal_title}\n*Score:* {score}\n[View Project]({url})"
             self._send_request(msg)
             self._last_sent[key] = time.time()

    def notify_bid_sent(self, proposal_title, mode):
        self._send_request(f"🚀 *LANCE ENVIADO* ({mode})\n\n*Projeto:* {proposal_title}")

if __name__ == "__main__":
    # Test Singleton
    bot1 = TelegramCommander()
    bot2 = TelegramCommander()
    assert bot1 is bot2

    bot1.notify_start_hunting()
    bot1.notify_high_score("Test Job", 95, "http://test.com")
    bot1.notify_high_score("Test Job", 95, "http://test.com") # Should be blocked by cooldown
