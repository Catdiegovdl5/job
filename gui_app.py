import customtkinter as ctk
import os, glob, subprocess, sys, threading
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class SniperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jules Sniper - S-Tier")
        self.geometry("900x500")
        
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="Munição Pronta (Pasta: output/)")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkButton(self, text="🔄 Atualizar Radar", command=self.refresh).pack(pady=10)
        self.refresh()

    def refresh(self):
        for w in self.main_frame.winfo_children(): w.destroy()
        files = glob.glob("output/*.txt")
        files.sort(key=os.path.getmtime, reverse=True)
        
        if not files: 
            ctk.CTkLabel(self.main_frame, text="Nenhuma proposta. Rode o 'python3 sentinel.py'").pack(pady=20)
            return
        
        for f in files:
            try:
                with open(f, 'r') as file: title = file.readline().replace("TITLE:", "").strip()
            except: title = "Sem Título"
            
            row = ctk.CTkFrame(self.main_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=title[:60]+"...").pack(side="left", padx=10)
            
            ctk.CTkButton(row, text="LANÇAR 🚀", width=100, fg_color="#00cc00", command=lambda x=f: self.launch(x)).pack(side="right", padx=5)
            ctk.CTkButton(row, text="Ver", width=50, command=lambda x=f: self.open_file(x)).pack(side="right", padx=5)

    def open_file(self, f):
        if sys.platform == "win32": os.startfile(f)
        else: subprocess.call(('xdg-open', f))

    def launch(self, f):
        threading.Thread(target=lambda: subprocess.run([sys.executable, "src/bidder.py", f])).start()

if __name__ == "__main__":
    app = SniperApp()
    app.mainloop()
