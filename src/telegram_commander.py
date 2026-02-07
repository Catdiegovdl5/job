import os
import time

# Mocking Telegram Commander for now as it wasn't present
class TelegramCommander:
    def __init__(self):
        self.is_hunting = False
        self.token = os.getenv("TELEGRAM_TOKEN", "mock_token")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "mock_chat_id")

    def send_message(self, text):
        print(f"[TELEGRAM] Sending to {self.chat_id}: {text}")
        # Here we would use requests.post to Telegram API

    def notify_start_hunting(self):
        if not self.is_hunting:
            self.send_message("Sniper Scout: Pronto para caçar! 🦅")
            self.is_hunting = True

    def notify_stop_hunting(self):
        if self.is_hunting:
            self.send_message("Sniper Scout: Pausando a caça. 💤")
            self.is_hunting = False

    def notify_high_score(self, proposal_title, score):
        if int(score) > 80:
             self.send_message(f"🎯 ALVO ENCONTRADO!\nTitle: {proposal_title}\nScore: {score}")

if __name__ == "__main__":
    bot = TelegramCommander()
    bot.notify_start_hunting()
    bot.notify_high_score("Test Job", 95)
    bot.notify_high_score("Low Job", 50)
    bot.notify_start_hunting() # Should not send duplicate
