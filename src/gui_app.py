import customtkinter as ctk
import os
import glob
import subprocess
import threading
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sniper Scout GUI")
        self.geometry("1000x600")

        self.tabview = ctk.CTkTabview(self, width=900, height=500)
        self.tabview.pack(padx=20, pady=20, expand=True, fill="both")

        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_bidding = self.tabview.add("Central de Lances")

        self.processing_files = set()

        self.setup_bidding_tab()

        # Initial Load
        self.refresh_table()

    def setup_bidding_tab(self):
        # Header
        self.header_frame = ctk.CTkFrame(self.tab_bidding)
        self.header_frame.pack(fill="x", padx=10, pady=5)

        self.refresh_btn = ctk.CTkButton(self.header_frame, text="Refresh List", command=self.refresh_table)
        self.refresh_btn.pack(side="left", padx=10)

        self.sniper_var = ctk.BooleanVar(value=False)
        self.sniper_switch = ctk.CTkSwitch(self.header_frame, text="Sniper Automático", variable=self.sniper_var, command=self.check_auto_sniper)
        self.sniper_switch.pack(side="right", padx=10)

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

    def refresh_table(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        files = glob.glob("propostas_geradas/WAITING_APPROVAL_*.txt")
        self.update_status(f"Found {len(files)} proposals.")

        for filepath in files:
            meta = self.parse_file(filepath)
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=2)

            # Columns
            ctk.CTkLabel(row, text=meta.get("CORE", "N/A"), width=150).pack(side="left", expand=True, fill="x")

            score_val = meta.get("SCORE", "0")
            ctk.CTkLabel(row, text=score_val, width=150).pack(side="left", expand=True, fill="x")

            ctk.CTkLabel(row, text=meta.get("TITLE", "Unknown"), width=150).pack(side="left", expand=True, fill="x")

            if filepath in self.processing_files:
                 ctk.CTkLabel(row, text="PROCESSING...", width=150, text_color="orange").pack(side="left", expand=True, fill="x")
            else:
                action_btn = ctk.CTkButton(row, text="🚀 LANÇAR LANCE", fg_color="green", width=150,
                                         command=lambda f=filepath: self.launch_bid(f))
                action_btn.pack(side="left", expand=True, fill="x", padx=5)

                # Auto-Sniper Check
                if self.sniper_var.get():
                    try:
                        if int(score_val) >= 85:
                            self.launch_bid(filepath)
                    except ValueError:
                        pass

    def launch_bid(self, filepath):
        if filepath in self.processing_files:
            return

        self.processing_files.add(filepath)
        self.refresh_table() # Update UI to show processing status immediately

        self.update_status(f"Launching bid for {os.path.basename(filepath)}...")

        def run_script():
            try:
                # Using sys.executable to ensure we use the same python environment
                process = subprocess.Popen(
                    [sys.executable, "src/bidder.py", filepath],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # Read output live
                for line in process.stdout:
                    self.update_status(line.strip())

                process.wait()
                rc = process.returncode

                if rc == 0:
                    self.update_status("Bid Processed Successfully!")
                else:
                    stderr = process.stderr.read()
                    self.update_status(f"Error: {stderr}")
            except Exception as e:
                 self.update_status(f"Exception: {str(e)}")
            finally:
                if filepath in self.processing_files:
                    self.processing_files.remove(filepath)
                # Refresh UI after a short delay to remove the processed item
                self.after(2000, self.refresh_table)

        threading.Thread(target=run_script, daemon=True).start()

    def update_status(self, msg):
        self.after(0, lambda: self.status_label.configure(text=msg))

    def check_auto_sniper(self):
        if self.sniper_var.get():
            self.refresh_table()

if __name__ == "__main__":
    app = App()
    print("[SYSTEM] Central de Lances ready for input.")
    app.mainloop()
