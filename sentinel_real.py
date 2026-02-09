import time
import logging
import subprocess
import os
import threading
import http.server
import socketserver
import telebot
from telebot import types
from src.proposal_generator import generate_proposal
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects, place_project_bid
from freelancersdk.resources.projects.helpers import create_search_projects_filter
from freelancersdk.resources.users.users import get_self_user_id

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("SentinelReal")

# Telegram Configuration
TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")

bot = telebot.TeleBot(TG_TOKEN) if TG_TOKEN else None

# Memory Handling
SEEN_FILE = "seen_projects.txt"

def load_seen_projects():
    if not os.path.exists(SEEN_FILE):
        return set()
    try:
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def save_seen_project(project_id):
    try:
        with open(SEEN_FILE, "a") as f:
            f.write(f"{project_id}\n")
    except Exception as e:
        logger.error(f"⚠️ Failed to save seen project: {e}")

def sync_to_github():
    logger.info("🚀 Syncing to GitHub...")
    try:
        subprocess.run("git add output/*.txt seen_projects.txt", shell=True)
        subprocess.run("git commit -m 'Sniper Report: Sync'", shell=True)
        subprocess.run("git push origin main", shell=True)
        logger.info("✅ Sync complete!")
    except Exception as e:
        logger.warning(f"⚠️ Git Sync: {e}")

# HTTP Server for Render Port Binding
PORT = int(os.environ.get("PORT", 8080))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"JULES Sniper S-Tier: ONLINE")

def start_server():
    logger.info(f"🌍 Starting Health Check Server on port {PORT}")
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"❌ HTTP Server Error: {e}")

# Radar Logic
def process_radar():
    if not bot:
        logger.error("❌ Bot not initialized. Skipping radar.")
        return

    token = os.environ.get("FLN_OAUTH_TOKEN")
    if not token:
        logger.error("❌ FLN_OAUTH_TOKEN missing.")
        return

    if not os.path.exists("output"): os.makedirs("output")

    logger.info("📡 Scanning Freelancer.com Radar...")
    
    try:
        session = Session(oauth_token=token, url="https://www.freelancer.com")
        
        query = "python scraping automation"
        search_filter = create_search_projects_filter(sort_field='time_updated', project_types=['fixed'])
        
        result = search_projects(session, query=query, search_filter=search_filter)
        
        if result and 'projects' in result:
            projects = result['projects'][:5] # Check top 5
            seen = load_seen_projects()
            
            new_count = 0
            for p in projects:
                project_id = str(p.get('id'))
                if project_id in seen:
                    continue

                title = p.get('title')
                desc = p.get('preview_description')
                link = f"https://www.freelancer.com/projects/{p.get('seo_url')}"
                budget_info = p.get('budget', {})
                min_budget = budget_info.get('minimum', 30)
                max_budget = budget_info.get('maximum', 100)
                currency = p.get('currency', {}).get('code', 'USD')
                budget_str = f"{currency} {min_budget} - {max_budget}"
                
                logger.info(f"🎯 NEW TARGET: {title}")
                
                # Generate Proposal (AI)
                try:
                    proposal = generate_proposal("freelancer", f"{title}: {desc}", use_ai=True)
                except Exception as e:
                    logger.error(f"⚠️ AI Gen Error: {e}")
                    proposal = f"I am an expert in Python automation and can deliver this project. {desc}"

                # Save locally with metadata for bidding
                filename = f"output/REAL_JOB_{project_id}.txt"
                with open(filename, "w", encoding="utf-8") as f_out:
                    f_out.write(f"ID: {project_id}\nTITLE: {title}\nBUDGET_MIN: {min_budget}\nLINK: {link}\n\n{proposal}")
                
                # Update Memory
                save_seen_project(project_id)
                new_count += 1
                
                # Send to Telegram
                if CHAT_ID:
                    markup = types.InlineKeyboardMarkup()
                    btn_send = types.InlineKeyboardButton("🚀 Enviar", callback_data=f"send_{project_id}")
                    btn_ignore = types.InlineKeyboardButton("❌ Recusar", callback_data=f"ignore_{project_id}")
                    markup.add(btn_send, btn_ignore)
                    
                    msg = f"🎯 *ALVO DETECTADO*\n\n*Title:* {title}\n*Budget:* {budget_str}\n\n[View Project]({link})"
                    try:
                        bot.send_message(CHAT_ID, msg, parse_mode="Markdown", reply_markup=markup)
                    except Exception as e:
                        logger.error(f"⚠️ Telegram Send Error: {e}")

                time.sleep(15) # Rate limit

            if new_count > 0:
                sync_to_github()
            else:
                logger.info("⏳ No new targets.")
                
    except Exception as e:
        logger.error(f"❌ Radar Error: {e}")

def monitor_radar():
    while True:
        process_radar()
        logger.info("💤 Sleeping 15 minutes...")
        time.sleep(900)

# Bot Handlers
if bot:
    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        try:
            if call.data.startswith("ignore_"):
                project_id = call.data.split("_")[1]
                logger.info(f"❌ Project {project_id} ignored by user.")
                try:
                    bot.answer_callback_query(call.id, "Projeto ignorado.")
                    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
                except Exception as e:
                     logger.warning(f"⚠️ UI Update Error: {e}")

            elif call.data.startswith("send_"):
                project_id = int(call.data.split("_")[1])
                logger.info(f"🚀 Initiating LIVE BID Protocol for Project {project_id}...")
                
                # 1. Retrieve Proposal Data
                proposal_text = ""
                bid_amount = 30 # Fallback
                try:
                    with open(f"output/REAL_JOB_{project_id}.txt", "r") as f:
                        content = f.read()
                        # Extract proposal (last part after double newline)
                        parts = content.split("\n\n")
                        if len(parts) > 1:
                            proposal_text = parts[-1]
                        else:
                            proposal_text = content
                        
                        # Try to parse budget min from file header
                        for line in content.splitlines():
                            if line.startswith("BUDGET_MIN:"):
                                try:
                                    bid_amount = float(line.split(":")[1].strip())
                                except:
                                    pass
                except Exception as e:
                    logger.warning(f"⚠️ Proposal retrieval failed ({e}). Using emergency fallback.")
                    proposal_text = "I am an expert in Python automation and I can complete this task perfectly. Please check my profile."

                # 2. Execute LIVE BID via API
                try:
                    token = os.environ.get("FLN_OAUTH_TOKEN")
                    session = Session(oauth_token=token, url="https://www.freelancer.com")
                    my_user_id = get_self_user_id(session)
                    
                    logger.info(f"💸 Placing Bid: {bid_amount} on Project {project_id} for User {my_user_id}")
                    
                    place_project_bid(
                        session,
                        project_id=project_id,
                        bidder_id=my_user_id,
                        amount=bid_amount,
                        period=7,
                        milestone_percentage=100,
                        description=proposal_text
                    )
                    
                    bot.answer_callback_query(call.id, "✅ CONQUISTADO! Proposta enviada.")
                    bot.edit_message_text(f"✅ *LANCE ENVIADO!* (ID: {project_id})\nAmount: {bid_amount}", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
                    logger.info(f"💰 Bid placed successfully for project {project_id}")
                    
                except Exception as e:
                    logger.error(f"❌ FATAL BID ERROR: {e}")
                    bot.answer_callback_query(call.id, f"❌ Erro: {str(e)[:50]}")
                    
        except Exception as e:
            logger.error(f"⚠️ Callback Logic Error: {e}")

if __name__ == "__main__":
    # Start HTTP Server Thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Start Radar Thread
    radar_thread = threading.Thread(target=monitor_radar, daemon=True)
    radar_thread.start()
    
    # Start Bot Polling (Main Loop)
    if bot:
        logger.info("🤖 Jules Sniper S-Tier: LIVE FIRE MODE ENGAGED")
        if CHAT_ID:
            try:
                bot.send_message(CHAT_ID, "🦅 *Jules Sniper S-Tier: LIVE FIRE MODE ONLINE*\nReady to earn.", parse_mode="Markdown")
            except Exception as e:
                logger.warning(f"⚠️ Startup Msg Failed: {e}")
        try:
            bot.infinity_polling()
        except Exception as e:
            logger.error(f"❌ Polling Error: {e}")
            while True:
                time.sleep(60)
    else:
        logger.error("❌ Bot not configured. Exiting.")
        while True:
            time.sleep(60)
