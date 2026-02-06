import customtkinter as ctk
import subprocess
import threading
import queue
import os
import time
import sys
import re
from datetime import datetime
import tkinter.messagebox

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ArchitectApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Proposals Architect - Command Center")
        self.geometry("1000x700")

        # Dependency Check
        try:
            import telegram
        except ImportError:
            print("[CRITICAL ERROR] Módulo 'python-telegram-bot' não encontrado.")
            # Since CTk inherits from Tk, we can try using standard message box
            # But in headless/no-display env this might crash or be invisible.
            # We wrap it to be safe.
            try:
                tkinter.messagebox.showerror("Erro de Dependência", "O módulo 'python-telegram-bot' não está instalado.\nFuncionalidades de Telegram não funcionarão.")
            except:
                pass # Headless fallback

        # State Variables
        self.sniper_process = None
        self.commander_process = None
        self.log_queue = queue.Queue()
        self.bids_remaining = 23
        self.known_proposals = set() # Track proposals to detect new ones
        self.is_running = False

        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="ARCHITECT\nSNIPER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Bids Counter
        self.bids_label_title = ctk.CTkLabel(self.sidebar, text="BIDS RESTANTES", font=ctk.CTkFont(size=12))
        self.bids_label_title.grid(row=1, column=0, padx=20, pady=(10, 0))

        self.bids_value_label = ctk.CTkLabel(self.sidebar, text=str(self.bids_remaining), font=ctk.CTkFont(size=40, weight="bold"), text_color="#2CC985")
        self.bids_value_label.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Switches
        self.autopilot_switch = ctk.CTkSwitch(self.sidebar, text="Sniper Automático")
        self.autopilot_switch.grid(row=3, column=0, padx=20, pady=10)

        # Buttons
        self.start_btn = ctk.CTkButton(self.sidebar, text="START SYSTEM", command=self.start_system, fg_color="#2CC985", text_color="black", hover_color="#229A65")
        self.start_btn.grid(row=4, column=0, padx=20, pady=10)

        self.stop_btn = ctk.CTkButton(self.sidebar, text="STOP SYSTEM", command=self.stop_system, fg_color="#C92C2C", hover_color="#9A2222", state="disabled")
        self.stop_btn.grid(row=5, column=0, padx=20, pady=10)

        self.folder_btn = ctk.CTkButton(self.sidebar, text="OPEN FOLDER", command=self.open_folder)
        self.folder_btn.grid(row=7, column=0, padx=20, pady=10)

        self.quick_view_btn = ctk.CTkButton(self.sidebar, text="QUICK VIEW", command=self.quick_view)
        self.quick_view_btn.grid(row=8, column=0, padx=20, pady=(10, 20))

        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.table_label = ctk.CTkLabel(self.main_frame, text="ÚLTIMAS PROPOSTAS GERADAS", font=ctk.CTkFont(size=16, weight="bold"))
        self.table_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Table Header
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
        self.logs_label = ctk.CTkLabel(self.main_frame, text="LIVE LOGS (Unified)", font=ctk.CTkFont(size=14, weight="bold"))
        self.logs_label.grid(row=3, column=0, sticky="w", pady=(20, 5))

        self.log_textbox = ctk.CTkTextbox(self.main_frame, height=150, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_textbox.grid(row=4, column=0, sticky="ew")

        # Start polling loops
        self.update_log_display()
        self.poll_files()

        # Auto-Start Commander if possible? User said "Unified Launch".
        # Let's start Commander when "START SYSTEM" is clicked to keep it simple.

    def start_system(self):
        if self.is_running:
            return

        self.is_running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log_textbox.insert("end", "[SYSTEM] Inicializando subsistemas...\n")

        # 1. Start Telegram Commander
        self.start_commander()

        # 2. Start Sniper Scout
        self.start_sniper()

    def stop_system(self):
        # Stop Scout
        if self.sniper_process:
            self.sniper_process.terminate()
            self.sniper_process = None

        # Stop Commander
        if self.commander_process:
            self.commander_process.terminate()
            self.commander_process = None

        self.is_running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.log_textbox.insert("end", "[SYSTEM] Todos os sistemas interrompidos.\n")

    def start_commander(self):
        self.log_textbox.insert("end", "[SYSTEM] Iniciando Telegram Commander...\n")
        cmd = [sys.executable, "-u", "src/telegram_commander.py"]

        try:
            self.commander_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            # Thread to read output
            t = threading.Thread(target=self._read_process_output, args=(self.commander_process, "[COMMANDER]"))
            t.daemon = True
            t.start()
        except Exception as e:
            self.log_queue.put(f"[ERROR] Falha ao iniciar Commander: {e}\n")

    def start_sniper(self):
        autopilot = self.autopilot_switch.get()
        mode_str = "AUTOMÁTICO" if autopilot else "MANUAL"
        self.log_textbox.insert("end", f"[SYSTEM] Iniciando Sniper Scout (Modo: {mode_str})...\n")

        cmd = [sys.executable, "-u", "src/freelancer_scout.py"]
        if autopilot:
            cmd.append("--autopilot")

        try:
            self.sniper_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            # Thread to read output
            t = threading.Thread(target=self._read_process_output, args=(self.sniper_process, "[SNIPER]"))
            t.daemon = True
            t.start()
        except Exception as e:
            self.log_queue.put(f"[ERROR] Falha ao iniciar Sniper: {e}\n")

    def _read_process_output(self, process, prefix):
        """Generic reader for subprocess stdout."""
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log_queue.put(f"{prefix} {line}")
        except Exception:
            pass
        finally:
            if process:
                process.stdout.close()

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

        # Check specifically for SUBMITTED files to update bid count
        # and ANY proposal file to update table
        all_files = [f for f in os.listdir(directory) if f.endswith(".txt")]

        # Determine new ones
        new_files = set(all_files) - self.known_proposals

        if new_files:
            for f in new_files:
                self.known_proposals.add(f)

                # Check if it is a "final" proposal file (submitted or waiting) to add to table
                if f.startswith("proposta_") or f.startswith("WAITING_APPROVAL_") or f.startswith("SUBMITTED_"):
                    self.add_proposal_to_ui(os.path.join(directory, f))

                # If it is SUBMITTED, decrement bid counter (Action taken)
                if f.startswith("SUBMITTED_"):
                    self.decrement_bids()

        self.after(5000, self.poll_files)

    def decrement_bids(self):
        if self.bids_remaining > 0:
            self.bids_remaining -= 1
            self.bids_value_label.configure(text=str(self.bids_remaining))

            if self.bids_remaining > 10:
                self.bids_value_label.configure(text_color="#2CC985")
            elif self.bids_remaining > 5:
                self.bids_value_label.configure(text_color="#F1C40F")
            else:
                self.bids_value_label.configure(text_color="#C92C2C")

    def add_proposal_to_ui(self, filepath):
        core = "Unknown"
        filename = os.path.basename(filepath)
        # Clean up filename for display
        title = filename.replace("proposta_", "").replace("WAITING_APPROVAL_", "").replace("SUBMITTED_", "").replace(".txt", "").replace("_", " ")
        score = "-"

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r"--- PROPOSTA GERADA \(Núcleo: (.*?) \| Score: (\d+)\) ---", content)
                if match:
                    core = match.group(1).strip()
                    score = match.group(2).strip()
                else:
                    match_old = re.search(r"--- PROPOSTA GERADA \(Núcleo: (.*?)\) ---", content)
                    if match_old:
                        core = match_old.group(1).strip()
        except:
            pass

        row = len(self.known_proposals)

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
        if not self.known_proposals:
            return

        directory = "propostas_geradas"
        files = [os.path.join(directory, f) for f in self.known_proposals]
        if files:
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
