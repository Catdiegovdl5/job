import customtkinter as ctk
import os
import glob
import subprocess
import threading
import sys
import json
import time
import shutil
import psutil
import sqlite3
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

STATS_FILE = "data/stats.json"
DB_FILE = "data/sniper.db"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sniper Scout GUI - NOC System")
        self.geometry("1000x800")

        # Concurrency Control
        self.bid_semaphore = threading.Semaphore(2)

        # Initialize Data
        self.ensure_data()
        self.init_db()

        self.tabview = ctk.CTkTabview(self, width=900, height=700)
        self.tabview.pack(padx=20, pady=20, expand=True, fill="both")

        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_bidding = self.tabview.add("Central de Lances")
        self.tab_ai = self.tabview.add("AI Settings")
        self.tab_proxy = self.tabview.add("Proxy Config")

        self.processing_files = set()
        self.auto_sniper_active = False

        self.setup_dashboard_tab()
        self.setup_bidding_tab()
        self.setup_ai_tab()
        self.setup_proxy_tab()

        # Initial Load
        self.refresh_table()
        self.update_dashboard_metrics()
        self.monitor_resources()

    def ensure_data(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(STATS_FILE):
            with open(STATS_FILE, "w") as f:
                json.dump({"total_bids": 0, "bids_today": 0, "success_rate": 0}, f)

    def init_db(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS bids
                              (filepath TEXT PRIMARY KEY, title TEXT, core TEXT, score INTEGER, status TEXT, last_updated TIMESTAMP, error TEXT)''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Init Error: {e}")

    def get_stats(self):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"total_bids": 0, "bids_today": 0, "success_rate": 0}

    # --- TABS SETUP ---

    def setup_dashboard_tab(self):
        self.tab_dashboard.grid_columnconfigure((0, 1, 2), weight=1)

        # KPI Cards
        self.card_pending = ctk.CTkLabel(self.tab_dashboard, text="PENDENTES\n0", fg_color="#2b2b2b", corner_radius=10, height=80, font=("Arial", 16, "bold"))
        self.card_pending.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.card_sent = ctk.CTkLabel(self.tab_dashboard, text="ENVIADOS\n0", fg_color="#1f538d", corner_radius=10, height=80, font=("Arial", 16, "bold"))
        self.card_sent.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.card_resources = ctk.CTkLabel(self.tab_dashboard, text="RESOURCES\nCPU: 0% | RAM: 0%", fg_color="#2b2b2b", corner_radius=10, height=80, font=("Arial", 14, "bold"))
        self.card_resources.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Mode Selector
        self.mode_label = ctk.CTkLabel(self.tab_dashboard, text="MODO DE OPERAÇÃO:", font=("Arial", 14))
        self.mode_label.grid(row=1, column=0, columnspan=3, pady=(20, 5))

        self.mode_selector = ctk.CTkSegmentedButton(self.tab_dashboard,
                                                    values=["GHOST", "BLITZ", "SURGICAL", "DEBUG"],
                                                    command=self.change_mode)
        self.mode_selector.set("GHOST")
        self.mode_selector.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        # Kill Switch
        self.kill_btn = ctk.CTkButton(self.tab_dashboard, text="KILL ALL PLAYWRIGHT", fg_color="red", command=self.confirm_kill_playwright)
        self.kill_btn.grid(row=3, column=0, columnspan=3, pady=10)

        # Terminal Output
        self.terminal_out = ctk.CTkTextbox(self.tab_dashboard, height=250, fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.terminal_out.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.terminal_out.insert("0.0", "--- Sniper Scout NOC System Ready ---\n")

    def setup_ai_tab(self):
        ctk.CTkLabel(self.tab_ai, text="AI Configuration", font=("Arial", 18, "bold")).pack(pady=20)

        ctk.CTkLabel(self.tab_ai, text="Model:").pack(pady=5)
        self.ai_model = ctk.CTkComboBox(self.tab_ai, values=["gemini-pro", "gemini-ultra"])
        self.ai_model.set("gemini-pro")
        self.ai_model.pack(pady=5)

        ctk.CTkLabel(self.tab_ai, text="Temperature:").pack(pady=5)
        self.ai_temp = ctk.CTkSlider(self.tab_ai, from_=0, to=1, number_of_steps=10)
        self.ai_temp.set(0.7)
        self.ai_temp.pack(pady=5)

        ctk.CTkButton(self.tab_ai, text="Save Settings", command=self.save_ai_settings).pack(pady=20)

    def setup_proxy_tab(self):
        ctk.CTkLabel(self.tab_proxy, text="Proxy Configuration", font=("Arial", 18, "bold")).pack(pady=20)

        self.proxy_entry = ctk.CTkEntry(self.tab_proxy, placeholder_text="http://user:pass@host:port", width=400)
        self.proxy_entry.pack(pady=10)

        ctk.CTkButton(self.tab_proxy, text="Save Proxy", command=self.save_proxy_settings).pack(pady=10)

        self.proxy_status = ctk.CTkLabel(self.tab_proxy, text="No Proxy Configured", text_color="gray")
        self.proxy_status.pack(pady=10)

    def save_ai_settings(self):
        # Save to JSON or .env logic here
        self.log_to_console(f"[AI] Settings Saved: Model={self.ai_model.get()}, Temp={self.ai_temp.get()}")

    def save_proxy_settings(self):
        proxy = self.proxy_entry.get()
        # Save logic
        self.log_to_console(f"[PROXY] Configuration updated: {proxy}")
        self.proxy_status.configure(text="Proxy Active", text_color="green")

    def monitor_resources(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.card_resources.configure(text=f"RESOURCES\nCPU: {cpu}% | RAM: {ram}%")
        self.after(2000, self.monitor_resources)

    def change_mode(self, value):
        self.log_to_console(f"[SYSTEM] Mode switched to: {value}")

    def confirm_kill_playwright(self):
        confirm_window = ctk.CTkToplevel(self)
        confirm_window.title("CONFIRM KILL")
        confirm_window.geometry("300x150")

        lbl = ctk.CTkLabel(confirm_window, text="Are you sure you want to KILL\nall Playwright processes?", font=("Arial", 14, "bold"), text_color="red")
        lbl.pack(pady=20)

        btn_frame = ctk.CTkFrame(confirm_window)
        btn_frame.pack(fill="x", padx=20)

        btn_yes = ctk.CTkButton(btn_frame, text="YES, KILL", fg_color="red", command=lambda: [self.kill_playwright(), confirm_window.destroy()])
        btn_yes.pack(side="left", expand=True, padx=5)

        btn_no = ctk.CTkButton(btn_frame, text="Cancel", command=confirm_window.destroy)
        btn_no.pack(side="right", expand=True, padx=5)

    def kill_playwright(self):
        self.log_to_console("[SYSTEM] Killing all chromium processes...")
        try:
            subprocess.run(["pkill", "-9", "chromium"], check=False)
            subprocess.run(["pkill", "-9", "chrome"], check=False)
            self.log_to_console("[SYSTEM] Processes terminated.")
        except Exception as e:
            self.log_to_console(f"[ERROR] Failed to kill processes: {e}")

    def log_to_console(self, message):
        self.after(0, lambda: self._log_to_console_main(message))

    def _log_to_console_main(self, message):
        self.terminal_out.insert("end", f"{message}\n")
        self.terminal_out.see("end")

    def update_dashboard_metrics(self):
        # Pending
        pending_count = len(glob.glob("propostas_geradas/WAITING_APPROVAL_*.txt"))
        self.card_pending.configure(text=f"PENDENTES\n{pending_count}")

        # Sent / Stats
        stats = self.get_stats()
        self.card_sent.configure(text=f"ENVIADOS\n{stats.get('total_bids', 0)}")

        self.after(5000, self.update_dashboard_metrics)

    def setup_bidding_tab(self):
        # Header
        self.header_frame = ctk.CTkFrame(self.tab_bidding)
        self.header_frame.pack(fill="x", padx=10, pady=5)

        self.refresh_btn = ctk.CTkButton(self.header_frame, text="Refresh List", command=self.refresh_table)
        self.refresh_btn.pack(side="left", padx=10)

        self.sniper_var = ctk.BooleanVar(value=False)
        self.sniper_switch = ctk.CTkSwitch(self.header_frame, text="Sniper Automático", variable=self.sniper_var, command=self.check_auto_sniper)
        self.sniper_switch.pack(side="right", padx=10)

        self.show_debug_var = ctk.BooleanVar(value=False)
        self.show_debug_chk = ctk.CTkCheckBox(self.header_frame, text="Show All (Debug)", variable=self.show_debug_var, command=self.refresh_table)
        self.show_debug_chk.pack(side="right", padx=10)

        self.status_label = ctk.CTkLabel(self.header_frame, text="Ready", text_color="gray", width=400, anchor="w")
        self.status_label.pack(side="left", padx=20, fill="x", expand=True)

        # Table Header
        self.table_header = ctk.CTkFrame(self.tab_bidding, height=30)
        self.table_header.pack(fill="x", padx=10, pady=(5,0))

        cols = ["Core", "Score", "Título da Vaga", "AÇÃO"]
        for col in cols:
            lbl = ctk.CTkLabel(self.table_header, text=col, font=("Arial", 12, "bold"), width=150)
            lbl.pack(side="left", expand=True, fill="x")

        # Table Body (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_bidding, width=900, height=400)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def parse_file(self, filepath):
        meta = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() == '---':
                        break
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            meta[parts[0].strip().upper()] = parts[1].strip()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
        return meta

    def trash_proposal(self, filepath):
        try:
            os.remove(filepath)
            status_file = filepath + ".status"
            if os.path.exists(status_file):
                os.remove(status_file)
            self.update_status(f"Deleted: {os.path.basename(filepath)}")
            self.refresh_table()
        except Exception as e:
            self.update_status(f"Error deleting: {e}")

    def refresh_table(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        files = glob.glob("propostas_geradas/WAITING_APPROVAL_*.txt")
        self.update_status(f"Found {len(files)} proposals.")

        for filepath in files:
            meta = self.parse_file(filepath)
            title = meta.get("TITLE", "Unknown")
            score_val = meta.get("SCORE", "0")

            # FILTER: Hide Unknowns unless Debug checked
            if not self.show_debug_var.get():
                if title == "Unknown" or score_val == "0":
                    continue

            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=2)

            # Columns
            ctk.CTkLabel(row, text=meta.get("CORE", "N/A"), width=150).pack(side="left", expand=True, fill="x")
            ctk.CTkLabel(row, text=score_val, width=150).pack(side="left", expand=True, fill="x")
            ctk.CTkLabel(row, text=title, width=150).pack(side="left", expand=True, fill="x")

            # Status Logic (Hybrid: DB + File)
            status_text = ""
            status_color = "gray"

            # Check DB first
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT status, error FROM bids WHERE filepath=?", (filepath,))
                res = cursor.fetchone()
                conn.close()
                if res:
                    status_text = res[0]
                    if "PROCESSING" in status_text:
                         status_color = "orange"
                    elif "SENT" in status_text:
                         status_color = "green"
                    elif "FAILED" in status_text:
                         status_color = "red"
            except:
                pass

            # Fallback to File if DB empty
            if not status_text:
                status_file = filepath + ".status"
                if os.path.exists(status_file):
                    with open(status_file, "r") as f:
                        content = f.read().strip()
                    if "PROCESSING" in content:
                        status_text = "⏳ " + content.replace("PROCESSING: ", "")[:15]
                        status_color = "orange"
                    elif "SENT" in content:
                        status_text = "✅ ENVIADO"
                        status_color = "green"
                    elif "FAILED" in content:
                        status_text = "❌ FALHA"
                        status_color = "red"

            if status_text:
                ctk.CTkLabel(row, text=status_text, text_color=status_color, width=150).pack(side="left", expand=True, fill="x")
            elif filepath in self.processing_files:
                 ctk.CTkLabel(row, text="QUEUED...", width=150, text_color="orange").pack(side="left", expand=True, fill="x")
            else:
                # ACTION BUTTONS
                action_frame = ctk.CTkFrame(row, fg_color="transparent")
                action_frame.pack(side="left", expand=True, fill="x")

                launch_btn = ctk.CTkButton(action_frame, text="🚀", fg_color="green", width=60,
                                         command=lambda f=filepath: self.launch_bid(f))
                launch_btn.pack(side="left", padx=5)

                trash_btn = ctk.CTkButton(action_frame, text="🗑️", fg_color="red", width=60,
                                         command=lambda f=filepath: self.trash_proposal(f))
                trash_btn.pack(side="left", padx=5)

                # Auto-Sniper Check
                if self.sniper_var.get():
                    try:
                        if int(score_val) >= 85:
                            self.launch_bid(filepath)
                    except ValueError:
                        pass

        self.update_dashboard_metrics() # Ensure dashboard is in sync
        # Polling for Auto-Sniper and Status Updates
        self.after(5000, self.refresh_table)

    def launch_bid(self, filepath):
        if filepath in self.processing_files:
            return

        mode = self.mode_selector.get()
        self.log_to_console(f"--- Queueing Bid: {os.path.basename(filepath)} [Mode: {mode}] ---")

        self.processing_files.add(filepath)
        self.refresh_table()

        self.update_status(f"Queueing bid for {os.path.basename(filepath)}...")

        def run_script():
            with self.bid_semaphore: # CONCURRENCY LIMIT
                try:
                    env = os.environ.copy()
                    env["SNIPER_MODE"] = mode

                    # Using sys.executable to ensure we use the same python environment
                    process = subprocess.Popen(
                        [sys.executable, "src/bidder.py", filepath],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                        env=env
                    )

                    # Read output live
                    for line in process.stdout:
                        line = line.strip()
                        self.update_status(line)
                        self.log_to_console(f"[BIDDER] {line}")

                    process.wait()
                    rc = process.returncode

                    if rc == 0:
                        self.update_status("Bid Processed Successfully!")
                        self.log_to_console("[SUCCESS] Bid Processed Successfully!")
                        self.increment_stats()

                        try:
                            subprocess.run(["notify-send", "Sniper Scout", f"Bid Sent: {os.path.basename(filepath)}"], check=False)
                        except:
                            pass
                    else:
                        stderr = process.stderr.read()
                        self.update_status(f"Error: {stderr}")
                        self.log_to_console(f"[ERROR] {stderr}")

                except Exception as e:
                     self.update_status(f"Exception: {str(e)}")
                     self.log_to_console(f"[EXCEPTION] {str(e)}")
                finally:
                    if filepath in self.processing_files:
                        self.processing_files.remove(filepath)
                    self.after(2000, self.refresh_table)

        threading.Thread(target=run_script, daemon=True).start()

    def increment_stats(self):
        try:
            with open(STATS_FILE, "r+") as f:
                data = json.load(f)
                data["total_bids"] = data.get("total_bids", 0) + 1
                data["bids_today"] = data.get("bids_today", 0) + 1
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        except Exception as e:
            self.log_to_console(f"[ERROR] Stats update failed: {e}")

    def update_status(self, msg):
        self.after(0, lambda: self.status_label.configure(text=msg))

    def check_auto_sniper(self):
        if self.sniper_var.get():
            self.refresh_table()

if __name__ == "__main__":
    app = App()
    print("[SYSTEM] Central de Lances ready for input.")
    app.mainloop()
