import customtkinter as ctk
import os
import sys
import glob
import subprocess
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [GUI] - %(levelname)s - %(message)s')

class SniperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sniper Command Center")
        self.geometry("800x600")

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Add tabs
        self.tabview.add("Dashboard")
        self.tabview.add("Central de Lances")

        # Setup Dashboard Tab
        self.setup_dashboard_tab()

        # Setup Central de Lances Tab
        self.setup_central_lances_tab()

    def setup_dashboard_tab(self):
        """
        Sets up the Dashboard tab with placeholder controls.
        """
        self.dashboard_frame = self.tabview.tab("Dashboard")
        self.dashboard_frame.grid_columnconfigure(0, weight=1)

        self.label_dashboard = ctk.CTkLabel(self.dashboard_frame, text="Sniper Scout Status: STANDBY", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_dashboard.grid(row=0, column=0, padx=20, pady=20)

        self.btn_start_scout = ctk.CTkButton(self.dashboard_frame, text="Start Scout Mission", command=self.start_scout)
        self.btn_start_scout.grid(row=1, column=0, padx=20, pady=10)

    def setup_central_lances_tab(self):
        """
        Sets up the Central de Lances tab with a dynamic list and refresh button.
        """
        self.pending_frame = self.tabview.tab("Central de Lances")
        self.pending_frame.grid_columnconfigure(0, weight=1)
        self.pending_frame.grid_rowconfigure(1, weight=1) # List area expands

        # Control Bar
        self.control_frame = ctk.CTkFrame(self.pending_frame)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_refresh = ctk.CTkButton(self.control_frame, text="Refresh List", command=self.refresh_list)
        self.btn_refresh.pack(side="left", padx=10, pady=10)

        # Scrollable List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self.pending_frame, label_text="Waiting for Approval")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Initial Load
        self.refresh_list()
        print("[SYSTEM] Central de Lances ready for input.")

    def start_scout(self):
        """
        Starts the scout process in a separate thread.
        """
        logging.info("Starting Scout process...")
        threading.Thread(target=self._run_scout_process, daemon=True).start()

    def _run_scout_process(self):
        try:
            subprocess.run([sys.executable, "src/scout.py"], check=True)
            logging.info("Scout process finished.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Scout process failed: {e}")

    def refresh_list(self):
        """
        Scans the directory for pending bids and repopulates the list.
        Uses try-except to handle race conditions where files might be deleted mid-scan.
        """
        try:
            # Clear existing widgets in scroll_frame
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()

            # Scan for files
            files = glob.glob("propostas_geradas/WAITING_APPROVAL_*.txt")
            logging.info(f"Found {len(files)} pending bids.")

            if not files:
                lbl = ctk.CTkLabel(self.scroll_frame, text="No pending bids found.")
                lbl.pack(pady=20)
                return

            for filepath in files:
                try:
                    if os.path.exists(filepath):
                        self.create_bid_row(filepath)
                except Exception as e:
                    logging.warning(f"Error displaying row for {filepath}: {e}")

        except Exception as e:
            logging.error(f"Error refreshing list: {e}")

    def create_bid_row(self, filepath):
        """
        Creates a row in the scrollable frame for a single bid file.
        """
        filename = os.path.basename(filepath)
        # Extract "Job Title" from filename (assuming format WAITING_APPROVAL_JobTitle.txt)
        display_name = filename.replace("WAITING_APPROVAL_", "").replace(".txt", "").replace("_", " ")

        row_frame = ctk.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", padx=5, pady=5)

        lbl_title = ctk.CTkLabel(row_frame, text=display_name, anchor="w")
        lbl_title.pack(side="left", padx=10, expand=True, fill="x")

        btn_send = ctk.CTkButton(row_frame, text="🚀 SEND BID", width=100, fg_color="green",
                                 command=lambda fp=filepath: self.send_bid(fp))
        btn_send.pack(side="right", padx=5)

        btn_trash = ctk.CTkButton(row_frame, text="🗑️ TRASH", width=100, fg_color="red",
                                  command=lambda fp=filepath: self.delete_bid(fp))
        btn_trash.pack(side="right", padx=5)

    def send_bid(self, filepath):
        """
        Triggers the bidder process for the given file.
        """
        logging.info(f"Sending bid for: {filepath}")
        threading.Thread(target=self._run_bidder_process, args=(filepath,), daemon=True).start()

        # Optimistic UI update: Remove the row immediately or on refresh
        # For simplicity, we refresh after a short delay or let the user refresh manually.
        # But a manual refresh is safer to confirm it's gone.
        self.after(1500, self.refresh_list)

    def _run_bidder_process(self, filepath):
        try:
            subprocess.run([sys.executable, "src/bidder.py", filepath], check=True)
            logging.info(f"Bid sent successfully for {filepath}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Bidder process failed: {e}")

    def delete_bid(self, filepath):
        """
        Deletes the bid file.
        """
        try:
            os.remove(filepath)
            logging.info(f"Deleted file: {filepath}")
            self.refresh_list()
        except OSError as e:
            logging.error(f"Error deleting file {filepath}: {e}")

if __name__ == "__main__":
    app = SniperGUI()
    app.mainloop()
