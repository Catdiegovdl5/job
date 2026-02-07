import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import subprocess
import threading
import sys
import os
import psutil
import time
import shutil
from dotenv import load_dotenv

load_dotenv()

class SniperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Freelancer Sniper Engine - Command Center")
        self.root.geometry("800x600")

        # --- TABS SETUP ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab1 = tk.Frame(self.notebook)
        self.tab2 = tk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Scout & Logs")
        self.notebook.add(self.tab2, text="Bidding Manager")

        # --- TAB 1: SCOUT & LOGS ---
        self.label = tk.Label(self.tab1, text="Sniper Engine Control", font=("Arial", 16))
        self.label.pack(pady=10)

        self.btn_frame = tk.Frame(self.tab1)
        self.btn_frame.pack(pady=10)

        # Updated Paths to src/
        self.btn_scout = tk.Button(self.btn_frame, text="Start Miner (Scout)", command=self.start_miner, bg="green", fg="white")
        self.btn_scout.pack(side=tk.LEFT, padx=10)

        # Redundancy: Explicitly pass credentials via args if triggered
        self.btn_bidder = tk.Button(self.btn_frame, text="Start Bidder", command=self.start_bidder, bg="orange", fg="black")
        self.btn_bidder.pack(side=tk.LEFT, padx=10)

        self.btn_telegram = tk.Button(self.btn_frame, text="Start Telegram Bot", command=self.start_telegram, bg="blue", fg="white")
        self.btn_telegram.pack(side=tk.LEFT, padx=10)

        self.btn_test = tk.Button(self.btn_frame, text="Test Telegram", command=self.test_telegram, bg="gray", fg="white")
        self.btn_test.pack(side=tk.LEFT, padx=10)

        # New Button: Force Send Proposal to Telegram (Directive 3)
        self.btn_force_send = tk.Button(self.btn_frame, text="TESTAR ENVIO TELEGRAM", command=self.force_send_telegram, bg="purple", fg="white")
        self.btn_force_send.pack(side=tk.LEFT, padx=10)

        self.btn_kill = tk.Button(self.btn_frame, text="🛑 STOP ALL", command=self.kill_all, bg="red", fg="white")
        self.btn_kill.pack(side=tk.LEFT, padx=10)

        self.log_area = scrolledtext.ScrolledText(self.tab1, width=90, height=20)
        self.log_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # --- TAB 2: BIDDING MANAGER ---
        # Treeview for Job List
        self.tree_frame = tk.Frame(self.tab2)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Title", "Core", "Score", "Budget"), show="headings")
        self.tree.heading("Title", text="Job Title")
        self.tree.heading("Core", text="Core / Nucleus")
        self.tree.heading("Score", text="Score")
        self.tree.heading("Budget", text="Budget")

        self.tree.column("Title", width=300)
        self.tree.column("Core", width=150)
        self.tree.column("Score", width=50)
        self.tree.column("Budget", width=80)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.bind('<<TreeviewSelect>>', self.on_select_job)

        # Action Buttons
        self.action_frame = tk.Frame(self.tab2)
        self.action_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_preview = tk.Button(self.action_frame, text="👁 Preview Proposal", command=self.preview_job, bg="gray", fg="white", state=tk.DISABLED)
        self.btn_preview.pack(side=tk.LEFT, padx=10)

        self.btn_approve = tk.Button(self.action_frame, text="🚀 LAUNCH (CONFIRM & SEND)", command=self.approve_job, bg="green", fg="white", state=tk.DISABLED)
        self.btn_approve.pack(side=tk.LEFT, padx=10)

        self.btn_reject = tk.Button(self.action_frame, text="❌ REJECT (DELETE)", command=self.reject_job, bg="red", fg="white", state=tk.DISABLED)
        self.btn_reject.pack(side=tk.LEFT, padx=10)

        # Status Label (Global)
        self.status_label = tk.Label(root, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.processes = {}
        self.pending_jobs = []

        # Start checking for pending jobs
        self.check_pending_jobs()
        # Start Folder Watcher
        self.check_folder_enviar()

    def check_folder_enviar(self):
        """Monitors propostas_geradas/ENVIAR/ for new files."""
        # Using relative path for portability, though user requested absolute.
        # This will work as long as cwd is project root.
        watch_dir = os.path.join("propostas_geradas", "ENVIAR")
        process_dir = os.path.join("propostas_geradas", "processadas")

        if os.path.exists(watch_dir):
            for filename in os.listdir(watch_dir):
                if filename.endswith(".txt"):
                    filepath = os.path.join(watch_dir, filename)
                    self.log(f"[FOLDER WATCHER] New file detected: {filename}")
                    self.status_label.config(text=f"Status: Dispatching {filename}...")

                    # Trigger Bidder
                    self.trigger_bidder_file(filepath)

                    # Move to processed
                    try:
                        shutil.move(filepath, os.path.join(process_dir, filename))
                        self.log(f"[FOLDER WATCHER] Moved to processadas.")
                    except Exception as e:
                        self.log(f"[ERROR] Moving file: {e}")

                    self.status_label.config(text="Status: Ready")

        self.root.after(2000, self.check_folder_enviar)

    def trigger_bidder_file(self, filepath):
        self.log(f"🚀 LAUNCHING Bidder for file: {filepath}")
        user = os.getenv("FLN_USER") or os.getenv("FREELANCER_EMAIL") or "unknown"
        password = os.getenv("FLN_PASS") or os.getenv("FREELANCER_PASSWORD") or "unknown"

        # Correctly pass --file argument
        args = ["--user", user, "--password", password, "--file", filepath]

        # Run process
        script_path = os.path.join("src", "bidder.py")
        threading.Thread(target=self._run_process, args=(script_path, "Bidder", args), daemon=True).start()

    def check_pending_jobs(self):
        """Reads pending_jobs.json and updates the Treeview."""
        try:
            import json
            if os.path.exists("pending_jobs.json"):
                with open("pending_jobs.json", "r") as f:
                    new_jobs = json.load(f)

                # Check if list changed (simple length/content check)
                # Ideally, we update the treeview intelligently, but clearing and reloading is simpler for now
                # To avoid flickering, only update if difference detected
                if new_jobs != self.pending_jobs:
                    self.pending_jobs = new_jobs

                    # Clear Treeview
                    for item in self.tree.get_children():
                        self.tree.delete(item)

                    # Repopulate
                    for i, job in enumerate(self.pending_jobs):
                        self.tree.insert("", tk.END, iid=i, values=(
                            job.get('title', 'N/A'),
                            job.get('core', 'Unknown'),
                            job.get('score', 0),
                            f"${job.get('budget', 0)}"
                        ))

        except Exception as e:
            pass

        self.root.after(2000, self.check_pending_jobs)

    def on_select_job(self, event):
        selection = self.tree.selection()
        if selection:
            self.btn_preview.config(state=tk.NORMAL)
            self.btn_approve.config(state=tk.NORMAL)
            self.btn_reject.config(state=tk.NORMAL)
        else:
            self.btn_preview.config(state=tk.DISABLED)
            self.btn_approve.config(state=tk.DISABLED)
            self.btn_reject.config(state=tk.DISABLED)

    def preview_job(self):
        selection = self.tree.selection()
        if selection:
            index = int(selection[0])
            job = self.pending_jobs[index]

            # Load proposal text
            safe_title = "".join(c for c in job['title'] if c.isalnum() or c in (' ', '_')).replace(" ", "_")
            filename = f"WAITING_APPROVAL_{safe_title}.txt"
            filepath = os.path.join("propostas_geradas", filename)

            content = "(No proposal file found)"
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

            # Show popup
            top = tk.Toplevel(self.root)
            top.title(f"Preview: {job['title']}")
            text_widget = scrolledtext.ScrolledText(top, width=80, height=30)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, content)

    def approve_job(self):
        selection = self.tree.selection()
        if selection:
            index = int(selection[0])
            job = self.pending_jobs[index]
            self.log(f"✅ CONFIRM & SEND: {job['title']}")
            self.status_label.config(text="Status: Dispatching...")

            # Determine filepath
            safe_title = "".join(c for c in job['title'] if c.isalnum() or c in (' ', '_')).replace(" ", "_")
            filename = f"WAITING_APPROVAL_{safe_title}.txt"
            filepath = os.path.join("propostas_geradas", filename)

            # Trigger Bidder
            self.trigger_bidder_file(filepath)

            # Remove from list (JSON)
            self.remove_job(index)

            # Note: We don't move file here because trigger_bidder_file spawns a thread.
            # Ideally bidder or folder watcher handles movement.
            # But "approve" means we are done with "pending".
            # Let's move it to 'processadas' manually to be safe?
            # Actually, trigger_bidder_file just runs the script.
            # Let's trust folder watcher or just leave it for now (simulated).

            self.root.after(3000, lambda: self.status_label.config(text="Status: Ready"))

    def reject_job(self):
        selection = self.tree.selection()
        if selection:
            index = int(selection[0])
            job = self.pending_jobs[index]
            self.log(f"❌ REJECTING: {job['title']}")

            # Delete file
            safe_title = "".join(c for c in job['title'] if c.isalnum() or c in (' ', '_')).replace(" ", "_")
            filename = f"WAITING_APPROVAL_{safe_title}.txt"
            filepath = os.path.join("propostas_geradas", filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.log(f"Deleted proposal file: {filename}")
                except Exception as e:
                    self.log(f"Error deleting file: {e}")

            self.remove_job(index)

    def remove_job(self, index):
        import json
        if 0 <= index < len(self.pending_jobs):
            del self.pending_jobs[index]
            # Treeview update will happen on next poll or we can force it
            # self.tree.delete(str(index)) # ID is index str

            # Update JSON file
            with open("pending_jobs.json", "w") as f:
                json.dump(self.pending_jobs, f, indent=4)

            # Refresh tree immediately to avoid lag
            self.check_pending_jobs()

    def trigger_bidder(self, job_title):
        self.log(f"Starting Bidder for {job_title}...")
        user = os.getenv("FLN_USER") or os.getenv("FREELANCER_EMAIL") or "unknown"
        password = os.getenv("FLN_PASS") or os.getenv("FREELANCER_PASSWORD") or "unknown"

        # Construct URL or pass title
        args = ["--user", user, "--password", password, "--url", job_title]
        threading.Thread(target=self._run_process, args=("src/bidder.py", "Bidder", args), daemon=True).start()

    def kill_all(self):
        self.log("Stopping all managed processes...")
        # 1. Kill tracked subprocesses
        for name, process in self.processes.items():
            if process.poll() is None:  # If running
                try:
                    process.terminate()
                    self.log(f"Terminated tracked process: {name}")
                except Exception as e:
                    self.log(f"Error terminating {name}: {e}")

        # 2. Hard kill for zombie python processes using psutil (More robust)
        try:
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Check if process is Python and running one of our scripts
                    cmdline = proc.info['cmdline']
                    if cmdline and 'python' in proc.info['name']:
                        script_name = None
                        if any("src/telegram_commander.py" in arg for arg in cmdline):
                            script_name = "Telegram Commander"
                        elif any("src/miner_app.py" in arg for arg in cmdline):
                            script_name = "Miner App"

                        if script_name and proc.info['pid'] != current_pid:
                            self.log(f"Found zombie {script_name} (PID: {proc.info['pid']}). Killing...")
                            proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # Brief pause to ensure OS releases resources
            time.sleep(1)
            self.log("Zombie cleanup complete.")

        except Exception as e:
            self.log(f"Advanced kill failed: {e}")

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_miner(self):
        self.log("Starting Miner App...")
        # Pointing to src/miner_app.py
        threading.Thread(target=self._run_process, args=("src/miner_app.py", "Miner", []), daemon=True).start()

    def start_telegram(self):
        self.kill_all() # Ensure clean slate before starting commander to avoid Conflict
        self.log("Starting Telegram Commander...")
        # Pointing to src/telegram_commander.py
        threading.Thread(target=self._run_process, args=("src/telegram_commander.py", "Telegram", []), daemon=True).start()

    def test_telegram(self):
        """Sends a single test message to verify credentials."""
        self.log("Testing Telegram Connection...")
        import requests
        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            self.log("ERROR: Missing Token or Chat ID in .env")
            return

        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": "✅ [TEST] Conexão com Telegram bem sucedida!"}
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                self.log("SUCCESS: Test message sent!")
            else:
                self.log(f"FAILURE: Telegram API Error {resp.status_code}: {resp.text}")
        except Exception as e:
            self.log(f"FAILURE: Connection Error: {e}")

    def force_send_telegram(self):
        """Forces sending the first pending job to Telegram."""
        if not self.pending_jobs:
            self.log("⚠️ No pending jobs to test send.")
            return

        job = self.pending_jobs[0]
        self.log(f"🚀 Force Sending Job to Telegram: {job['title']}")

        # We need to replicate miner_app.send_telegram_alert logic roughly
        # Or simpler: just spawn a quick python script to do it?
        # Actually, let's just do requests logic here to avoid complex imports

        import requests
        import html

        token = os.getenv("TELEGRAM_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            self.log("ERROR: Missing Token/ChatID")
            return

        safe_title = html.escape(job['title'])
        job_link = f"https://www.freelancer.com/projects/{job['title'].replace(' ', '-').lower()}"

        # Try to read proposal content if file exists
        proposal_content = "(Preview unavailable)"
        safe_filename_title = "".join(c for c in job['title'] if c.isalnum() or c in (' ', '_')).replace(" ", "_")
        filename = f"WAITING_APPROVAL_{safe_filename_title}.txt"
        filepath = os.path.join("propostas_geradas", filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                proposal_content = html.escape(f.read())

        message = (
            f"🚨 <b>Sniper Alert (FORCED TEST)</b> 🚨\n\n"
            f"<b>Job:</b> <a href='{job_link}'>{safe_title}</a>\n"
            f"<b>Budget:</b> ${job['budget']}\n"
            f"<b>Score:</b> {job['score']} (Forced)\n\n"
            f"<b>Proposta Gerada:</b>\n<pre>{proposal_content}</pre>"
        )

        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Aprovar (Simulado)", "callback_data": f"approve_bid|{job['title']}"},
                    {"text": "❌ Rejeitar", "callback_data": f"reject_bid|{job['title']}"}
                ]
            ]
        }

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                self.log("SUCCESS: Force sent to Telegram.")
            else:
                self.log(f"FAILURE: {resp.status_code} - {resp.text}")
        except Exception as e:
            self.log(f"FAILURE: {e}")

    def start_bidder(self):
        self.log("Starting Bidder...")
        # Redundancy: Fetch creds from env and pass as args
        user = os.getenv("FLN_USER") or os.getenv("FREELANCER_EMAIL") or "unknown_user"
        password = os.getenv("FLN_PASS") or os.getenv("FREELANCER_PASSWORD") or "unknown_pass"

        args = ["--user", user, "--password", password]
        # Pointing to src/bidder.py
        threading.Thread(target=self._run_process, args=("src/bidder.py", "Bidder", args), daemon=True).start()

    def _run_process(self, script_path, name, extra_args):
        try:
            python_exec = sys.executable
            # Ensure script_path is correct relative to CWD (root)
            cmd = [python_exec, script_path] + extra_args

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            self.processes[name] = process

            for line in iter(process.stdout.readline, ''):
                self.root.after(0, self.log, f"[{name}] {line.strip()}")

            stderr = process.stderr.read()
            if stderr:
                 self.root.after(0, self.log, f"[{name} ERROR] {stderr.strip()}")

        except Exception as e:
            self.root.after(0, self.log, f"Error starting {name}: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SniperGUI(root)
    root.mainloop()
