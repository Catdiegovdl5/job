import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import os
import psutil
import time
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

        self.log_area = scrolledtext.ScrolledText(root, width=80, height=20)
        self.log_area.pack(pady=10)

        self.processes = {}

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
