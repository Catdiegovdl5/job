import os
import telebot

class TelegramCommander:
    def __init__(self):
        self.token = os.getenv("TG_TOKEN")
        self.chat_id = os.getenv("TG_CHAT_ID")
        self.bot = telebot.TeleBot(self.token) if self.token else None

    def send_alert(self, project, proposal):
        if not self.bot or not self.chat_id:
            print("Telegram not configured (TG_TOKEN or TG_CHAT_ID missing). Skipping alert.")
            print(f"Would have sent: {project.get('title', 'Unknown')}")
            return

        # Sanitize proposal for HTML to prevent parse errors
        # Replace < and > just in case, though <pre> handles most things, nested tags can break it.
        safe_proposal = proposal.replace("<", "&lt;").replace(">", "&gt;")

        # Sanitize description
        description = project.get('description', '') or ''
        safe_description = description.replace("<", "&lt;").replace(">", "&gt;")

        message = (
            f"🚨 <b>NEW LEAD DETECTED</b> 🚨\n\n"
            f"📌 <b>Project:</b> {project.get('title', 'Unknown')}\n"
            f"💰 <b>Budget:</b> ${project.get('budget', 'Unknown')}\n"
            f"🔗 <a href='{project.get('url', '#')}'>Link to Project</a>\n\n"
            f"📝 <b>Description:</b>\n{safe_description[:500]}...\n\n"
            f"--------------------\n\n"
            f"💡 <b>Generated Proposal:</b>\n<pre>{safe_proposal}</pre>"
        )

        try:
            self.bot.send_message(
                self.chat_id,
                message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            print(f"Alert sent for {project.get('title', 'Unknown')}")
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
