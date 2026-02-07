import tkinter as tk
from tkinter import scrolledtext
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
        self.root.geometry("700x500")

        self.label = tk.Label(root, text="Sniper Engine Control", font=("Arial", 16))
        self.label.pack(pady=10)

        self.btn_frame = tk.Frame(root)
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

        self.btn_kill = tk.Button(self.btn_frame, text="🛑 STOP ALL", command=self.kill_all, bg="red", fg="white")
        self.btn_kill.pack(side=tk.LEFT, padx=10)

        self.log_area = scrolledtext.ScrolledText(root, width=80, height=15)
        self.log_area.pack(pady=10)

        # --- NEW APPROVAL SECTION ---
        self.approval_frame = tk.LabelFrame(root, text="Pending Approvals", font=("Arial", 12))
        self.approval_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.approval_list = tk.Listbox(self.approval_frame, height=8)
        self.approval_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.approval_list.bind('<<ListboxSelect>>', self.on_select_job)

        self.action_frame = tk.Frame(self.approval_frame)
        self.action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.btn_approve = tk.Button(self.action_frame, text="🚀 LAUNCH", command=self.approve_job, bg="green", fg="white", state=tk.DISABLED)
        self.btn_approve.pack(fill=tk.X, pady=2)

        self.btn_reject = tk.Button(self.action_frame, text="❌ Reject", command=self.reject_job, bg="red", fg="white", state=tk.DISABLED)
        self.btn_reject.pack(fill=tk.X, pady=2)

        # Status Label
        self.status_label = tk.Label(self.root, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
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
        """Reads pending_jobs.json and updates the list."""
        try:
            import json
            if os.path.exists("pending_jobs.json"):
                with open("pending_jobs.json", "r") as f:
                    new_jobs = json.load(f)

                # Check if list changed
                current_titles = [j['title'] for j in self.pending_jobs]
                new_titles = [j['title'] for j in new_jobs]

                if current_titles != new_titles:
                    self.pending_jobs = new_jobs
                    self.approval_list.delete(0, tk.END)
                    for job in self.pending_jobs:
                        display_text = f"{job['title']} | ${job['budget']} | Score: {job['score']}"
                        self.approval_list.insert(tk.END, display_text)

        except Exception as e:
            pass # Silent fail to avoid spamming log

        self.root.after(2000, self.check_pending_jobs) # Poll every 2s

    def on_select_job(self, event):
        selection = self.approval_list.curselection()
        if selection:
            self.btn_approve.config(state=tk.NORMAL)
            self.btn_reject.config(state=tk.NORMAL)

            # Show proposal preview in log? Or maybe a popup?
            index = selection[0]
            job = self.pending_jobs[index]
            self.log(f"--- SELECTED: {job['title']} ---\n{job.get('description', '')[:200]}...")
        else:
            self.btn_approve.config(state=tk.DISABLED)
            self.btn_reject.config(state=tk.DISABLED)

    def approve_job(self):
        selection = self.approval_list.curselection()
        if selection:
            index = selection[0]
            job = self.pending_jobs[index]
            self.log(f"✅ APPROVING: {job['title']}")
            self.status_label.config(text="Status: Dispatching...")

            # Determine filepath (assumes miner logic)
            safe_title = "".join(c for c in job['title'] if c.isalnum() or c in (' ', '_')).replace(" ", "_")
            filename = f"WAITING_APPROVAL_{safe_title}.txt"
            filepath = os.path.join("propostas_geradas", filename)

            # Trigger Bidder
            self.trigger_bidder_file(filepath)

            # Remove from list
            self.remove_job(index)
            # Reset status later or immediately? Thread runs async so status might flicker.
            # Ideally trigger_bidder_file logic manages status but it's async.
            self.root.after(3000, lambda: self.status_label.config(text="Status: Ready"))

    def reject_job(self):
        selection = self.approval_list.curselection()
        if selection:
            index = selection[0]
            job = self.pending_jobs[index]
            self.log(f"❌ REJECTING: {job['title']}")
            self.remove_job(index)

    def remove_job(self, index):
        import json
        del self.pending_jobs[index]
        self.approval_list.delete(index)

        # Update JSON file
        with open("pending_jobs.json", "w") as f:
            json.dump(self.pending_jobs, f, indent=4)

        self.btn_approve.config(state=tk.DISABLED)
        self.btn_reject.config(state=tk.DISABLED)

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
