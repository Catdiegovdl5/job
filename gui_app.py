import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import sys
import os

class SniperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Freelancer Sniper Engine - Command Center")
        self.root.geometry("600x400")

        self.label = tk.Label(root, text="Sniper Engine Control", font=("Arial", 16))
        self.label.pack(pady=10)

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=10)

        # FIX: Unified command center to launch subprocesses
        self.btn_scout = tk.Button(self.btn_frame, text="Start Scout (Scraper)", command=self.start_scout, bg="green", fg="white")
        self.btn_scout.pack(side=tk.LEFT, padx=10)

        self.btn_telegram = tk.Button(self.btn_frame, text="Start Telegram Bot", command=self.start_telegram, bg="blue", fg="white")
        self.btn_telegram.pack(side=tk.LEFT, padx=10)

        self.log_area = scrolledtext.ScrolledText(root, width=70, height=15)
        self.log_area.pack(pady=10)

        self.scout_process = None
        self.telegram_process = None

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_scout(self):
        self.log("Starting Freelancer Scout...")
        # Running as subprocess
        threading.Thread(target=self._run_process, args=("freelancer_scout.py", "Scout"), daemon=True).start()

    def start_telegram(self):
        self.log("Starting Telegram Commander...")
        # Running as subprocess
        threading.Thread(target=self._run_process, args=("telegram_commander.py", "Telegram"), daemon=True).start()

    def _run_process(self, script_name, name):
        try:
            # Determine python executable
            python_exec = sys.executable
            process = subprocess.Popen(
                [python_exec, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            if name == "Scout":
                self.scout_process = process
            elif name == "Telegram":
                self.telegram_process = process

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
