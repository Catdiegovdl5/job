import customtkinter as ctk
import subprocess
import threading
import queue
import os
import time
import sys
import re
from datetime import datetime

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ArchitectApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Proposals Architect - Command Center")
        self.geometry("1000x700")

        # State Variables
        self.sniper_process = None
        self.log_queue = queue.Queue()
        self.bids_remaining = 23
        self.known_proposals = set()
        self.is_running = False

        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="ARCHITECT\nSNIPER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Bids Counter
        self.bids_label_title = ctk.CTkLabel(self.sidebar, text="BIDS RESTANTES", font=ctk.CTkFont(size=12))
        self.bids_label_title.grid(row=1, column=0, padx=20, pady=(10, 0))

        self.bids_value_label = ctk.CTkLabel(self.sidebar, text=str(self.bids_remaining), font=ctk.CTkFont(size=40, weight="bold"), text_color="#2CC985")
        self.bids_value_label.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Buttons
        self.start_btn = ctk.CTkButton(self.sidebar, text="START SNIPER", command=self.start_sniper, fg_color="#2CC985", text_color="black", hover_color="#229A65")
        self.start_btn.grid(row=5, column=0, padx=20, pady=10)

        self.stop_btn = ctk.CTkButton(self.sidebar, text="STOP SNIPER", command=self.stop_sniper, fg_color="#C92C2C", hover_color="#9A2222", state="disabled")
        self.stop_btn.grid(row=6, column=0, padx=20, pady=10)

        self.folder_btn = ctk.CTkButton(self.sidebar, text="OPEN FOLDER", command=self.open_folder)
        self.folder_btn.grid(row=7, column=0, padx=20, pady=10)

        self.quick_view_btn = ctk.CTkButton(self.sidebar, text="QUICK VIEW (Max Score)", command=self.quick_view)
        self.quick_view_btn.grid(row=8, column=0, padx=20, pady=(10, 20))

        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.table_label = ctk.CTkLabel(self.main_frame, text="ÚLTIMAS PROPOSTAS GERADAS", font=ctk.CTkFont(size=16, weight="bold"))
        self.table_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Table Header (Manual implementation for custom look)
        self.table_header = ctk.CTkFrame(self.main_frame, height=30)
        self.table_header.grid(row=1, column=0, sticky="new")
        self.table_header.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(self.table_header, text="CORE", width=80, anchor="w").grid(row=0, column=0, padx=10)
        ctk.CTkLabel(self.table_header, text="SCORE", width=60, anchor="center").grid(row=0, column=1, padx=10)
        ctk.CTkLabel(self.table_header, text="TÍTULO DA VAGA", anchor="w").grid(row=0, column=2, padx=10, sticky="ew")

        # Scrollable Proposals List
        self.scrollable_proposals = ctk.CTkScrollableFrame(self.main_frame, label_text="")
        self.scrollable_proposals.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        self.scrollable_proposals.grid_columnconfigure(2, weight=1)

        # --- Logs Area ---
        self.logs_label = ctk.CTkLabel(self.main_frame, text="LIVE LOGS", font=ctk.CTkFont(size=14, weight="bold"))
        self.logs_label.grid(row=3, column=0, sticky="w", pady=(20, 5))

        self.log_textbox = ctk.CTkTextbox(self.main_frame, height=150, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.grid(row=4, column=0, sticky="ew")

        # Start loops
        self.update_log_display()
        self.poll_files()

    def start_sniper(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log_textbox.insert("end", "[SYSTEM] Iniciando Sniper em thread separada...\n")

        # Start subprocess in thread
        self.thread = threading.Thread(target=self._run_scout_process)
        self.thread.daemon = True
        self.thread.start()

    def stop_sniper(self):
        if self.sniper_process:
            self.sniper_process.terminate()
            self.sniper_process = None

        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.log_textbox.insert("end", "[SYSTEM] Sniper interrompido pelo usuário.\n")

    def _run_scout_process(self):
        # Run python3 src/freelancer_scout.py
        # Capture unbuffered output
        cmd = [sys.executable, "-u", "src/freelancer_scout.py"]

        try:
            self.sniper_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in iter(self.sniper_process.stdout.readline, ''):
                self.log_queue.put(line)

            self.sniper_process.stdout.close()
            self.sniper_process.wait()

        except Exception as e:
            self.log_queue.put(f"[ERROR] Subprocess crash: {e}\n")
        finally:
            self.is_running = False
            # Needs to update UI from main thread logic, handled by buttons state in loop?
            # Simplified: buttons won't toggle back automatically here but that's ok for V1.

    def update_log_display(self):
        while not self.log_queue.empty():
            try:
                line = self.log_queue.get_nowait()
                self.log_textbox.insert("end", line)
                self.log_textbox.see("end")
            except queue.Empty:
                break

        self.after(100, self.update_log_display)

    def poll_files(self):
        """Polls the propostas_geradas folder for new files."""
        directory = "propostas_geradas"
        if not os.path.exists(directory):
            os.makedirs(directory)

        files = [f for f in os.listdir(directory) if (f.startswith("proposta_") or f.startswith("WAITING_APPROVAL_")) and f.endswith(".txt")]

        new_files = set(files) - self.known_proposals

        if new_files:
            for f in new_files:
                self.known_proposals.add(f)
                self.add_proposal_to_ui(os.path.join(directory, f))
                self.decrement_bids()

        self.after(5000, self.poll_files)

    def decrement_bids(self):
        if self.bids_remaining > 0:
            self.bids_remaining -= 1
            self.bids_value_label.configure(text=str(self.bids_remaining))

            if self.bids_remaining > 10:
                self.bids_value_label.configure(text_color="#2CC985") # Green
            elif self.bids_remaining > 5:
                self.bids_value_label.configure(text_color="#F1C40F") # Yellow
            else:
                self.bids_value_label.configure(text_color="#C92C2C") # Red

    def add_proposal_to_ui(self, filepath):
        # Extract info
        core = "Unknown"
        filename = os.path.basename(filepath)
        title = filename.replace("proposta_", "").replace("WAITING_APPROVAL_", "").replace(".txt", "").replace("_", " ")
        score = "-"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Updated Regex to capture Score from the new header format
                # --- PROPOSTA GERADA (Núcleo: Tech | Score: 75) ---
                match = re.search(r"--- PROPOSTA GERADA \(Núcleo: (.*?) \| Score: (\d+)\) ---", content)
                if match:
                    core = match.group(1).strip()
                    score = match.group(2).strip()
                else:
                    # Fallback for old files
                    match_old = re.search(r"--- PROPOSTA GERADA \(Núcleo: (.*?)\) ---", content)
                    if match_old:
                        core = match_old.group(1).strip()
        except:
            pass

        # Create Row
        row = len(self.known_proposals)

        # Color coding for Core
        core_color = "gray"
        if "Tech" in core: core_color = "#3498DB"
        elif "Data" in core: core_color = "#9B59B6"
        elif "Marketing" in core: core_color = "#E67E22"

        ctk.CTkLabel(self.scrollable_proposals, text=core, text_color=core_color, width=80, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.scrollable_proposals, text=score, width=60, anchor="center").grid(row=row, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.scrollable_proposals, text=title[:60], anchor="w").grid(row=row, column=2, padx=10, pady=5, sticky="ew")

    def open_folder(self):
        folder = "propostas_geradas"
        if not os.path.exists(folder):
            os.makedirs(folder)

        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def quick_view(self):
        # Open the latest generated proposal
        if not self.known_proposals:
            return

        # Find latest file by modification time
        directory = "propostas_geradas"
        files = [os.path.join(directory, f) for f in self.known_proposals]
        latest_file = max(files, key=os.path.getmtime)

        if sys.platform == "win32":
            os.startfile(latest_file)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", latest_file])
        else:
            subprocess.Popen(["xdg-open", latest_file])

if __name__ == "__main__":
    app = ArchitectApp()
    app.mainloop()
