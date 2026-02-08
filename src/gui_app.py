import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import threading
import queue
import sys

# Ensure proper module execution if run as script
try:
    from .worker import ServiceAgent
except ImportError:
    # Add parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.worker import ServiceAgent

# Initialize Agent
agent = ServiceAgent()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Jules Automation Hub")
        self.geometry("800x600")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_view.add("Central de Lances")
        self.tab_view.add("Gerar Trabalho")
        self.tab_view.add("Config")

        self.setup_work_generation_tab()

        # Thread-safe GUI updates
        self.msg_queue = queue.Queue()
        self.check_queue()

    def setup_work_generation_tab(self):
        tab = self.tab_view.tab("Gerar Trabalho")
        tab.grid_columnconfigure(0, weight=1)

        self.label_skill = ctk.CTkLabel(tab, text="Select Skill Category:")
        self.label_skill.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        self.skill_option = ctk.CTkOptionMenu(tab, values=["Excel/SQL", "SEO/Writing", "Marketing", "Python/Automation"])
        self.skill_option.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.label_desc = ctk.CTkLabel(tab, text="Project Instructions:")
        self.label_desc.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")

        self.text_desc = ctk.CTkTextbox(tab, height=200)
        self.text_desc.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")

        self.btn_generate = ctk.CTkButton(tab, text="🛠️ GERAR TRABALHO", command=self.start_generation)
        self.btn_generate.grid(row=4, column=0, padx=20, pady=20, sticky="ew")

        self.label_status = ctk.CTkLabel(tab, text="Ready", text_color="green")
        self.label_status.grid(row=5, column=0, padx=20, pady=5)

    def start_generation(self):
        skill = self.skill_option.get()
        instructions = self.text_desc.get("1.0", tk.END).strip()

        if not instructions:
            messagebox.showwarning("Input Error", "Please provide instructions.")
            return

        self.label_status.configure(text="Generating...", text_color="orange")
        self.btn_generate.configure(state="disabled")

        thread = threading.Thread(target=self.generate_work, args=(skill, instructions))
        thread.start()

    def generate_work(self, skill, instructions):
        try:
            result = agent.execute_task(skill, instructions)
            self.save_result(skill, instructions, result)
            self.msg_queue.put(("update_status", ("Success!", "green")))
            self.msg_queue.put(("show_info", ("Success", "Deliverable generated and saved!")))
        except Exception as e:
            self.msg_queue.put(("update_status", (f"Error: {str(e)}", "red")))
            self.msg_queue.put(("show_error", ("Error", str(e))))
        finally:
            self.msg_queue.put(("enable_button", None))

    def save_result(self, skill, instructions, result):
        if not os.path.exists("entregas"):
            os.makedirs("entregas")

        filename = f"entregas/delivery_{skill.replace('/', '_')}_{len(os.listdir('entregas')) + 1}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"SKILL: {skill}\n")
            f.write(f"INSTRUCTIONS:\n{instructions}\n")
            f.write("-" * 40 + "\n")
            f.write(result)

    def check_queue(self):
        try:
            while True:
                msg_type, data = self.msg_queue.get_nowait()
                if msg_type == "update_status":
                    text, color = data
                    self.label_status.configure(text=text, text_color=color)
                elif msg_type == "show_info":
                    title, msg = data
                    messagebox.showinfo(title, msg)
                elif msg_type == "show_error":
                    title, msg = data
                    messagebox.showerror(title, msg)
                elif msg_type == "enable_button":
                    self.btn_generate.configure(state="normal")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_queue)

if __name__ == "__main__":
    app = App()
    app.mainloop()
