import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import threading
import ollama
import subprocess
import random
import time
import os
import sys
import ctypes
from datetime import datetime

class DesktopBuddy:
    def __init__(self):
        self.root = tk.Tk()
        
        # Windows 11 Styling
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        self.transparent_color = "#abcdef" 
        self.root.config(bg=self.transparent_color)
        self.root.wm_attributes("-transparentcolor", self.transparent_color)

        # Bild laden & Pixel-Transparenz
        original_img = Image.open("buddy.png").convert("RGBA").resize((150, 150))
        datas = original_img.getdata()
        new_data = []
        for item in datas:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((0, 0, 0, 0))
            else:
                new_data.append(item)
        original_img.putdata(new_data)
        
        self.buddy_img = ImageTk.PhotoImage(original_img)
        self.label = tk.Label(self.root, image=self.buddy_img, bg=self.transparent_color)
        self.label.pack()

        self.root.geometry("150x150+300+300")

        # Events binden
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<Double-Button-1>", self.ask_ai_prompt)
        self.label.bind("<Button-3>", self.show_menu)

        self.ai_personality = "Du bist eine lustige Desktop-Banane. Antworte kurz auf Deutsch."

        # RECHTSKLICK-MENÜ
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="💬 KI Fragen (Doppelklick)", command=self.ask_ai_prompt)
        
        self.pers_menu = tk.Menu(self.menu, tearoff=0)
        self.pers_menu.add_command(label="😊 Freundlich", command=lambda: self.change_pers("Du bist eine freundliche Desktop-Banane."))
        self.pers_menu.add_command(label="😠 Genervt", command=lambda: self.change_pers("Du bist extrem genervt, antwortest frech und kurz."))
        self.pers_menu.add_command(label="🏴‍☠️ Hacker-Piraterie", command=lambda: self.change_pers("Du redest wie ein 90er-Hacker mit Piraten-Dialekt."))
        self.menu.add_cascade(label="🎭 KI Charakter ändern", menu=self.pers_menu)
        
        self.menu.add_separator()
        
        self.menu.add_command(label="📝 Datei vernichten", command=self.delete_file_command)
        self.menu.add_command(label="📂 Downloads öffnen", command=lambda: subprocess.Popen('explorer.exe shell:Downloads'))
        self.menu.add_command(label="⚙️ Task-Manager", command=lambda: subprocess.Popen('taskmgr.exe'))
        self.menu.add_command(label="🖥️ Windows Theme wechseln", command=self.toggle_windows_theme)
        self.menu.add_command(label="🔒 PC Sperren", command=lambda: ctypes.windll.user32.LockWorkStation())
        
        self.menu.add_separator()
        
        self.fun_menu = tk.Menu(self.menu, tearoff=0)
        self.fun_menu.add_command(label="🎮 Zahlen raten spielen", command=self.play_game)
        self.fun_menu.add_command(label="💥 JUMPSCARE!", command=self.trigger_jumpscare)
        self.menu.add_cascade(label="🎉 Spaß & Spiele", menu=self.fun_menu)

        self.menu.add_separator()
        self.menu.add_command(label="👋 Programm Beenden", command=self.root.destroy)

        self.is_busy = False
        threading.Thread(target=self.random_movement_loop, daemon=True).start()

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def speak_text(self, text):
        safe_text = text.replace('"', '').replace("'", "")
        cmd = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{safe_text}")'
        subprocess.run(["powershell", "-Command", cmd], capture_output=True)

    def crawl_to(self, target_x, target_y, speed_steps=60):
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        for i in range(speed_steps):
            next_x = current_x + int((target_x - current_x) * (i / speed_steps))
            next_y = current_y + int((target_y - current_y) * (i / speed_steps))
            self.root.after(0, lambda x=next_x, y=next_y: self.root.geometry(f"+{x}+{y}"))
            time.sleep(0.01)

    def change_pers(self, prompt):
        self.ai_personality = prompt
        self.speak_text("Charakter angepasst!")

    def toggle_windows_theme(self):
        cmd = 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name AppsUseLightTheme'
        res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        current_val = 1 if "1" in res.stdout else 0
        new_val = 0 if current_val == 1 else 1
        set_cmd = f'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name AppsUseLightTheme -Value {new_val}'
        subprocess.run(["powershell", "-Command", set_cmd])
        self.speak_text("Farbe geändert!")

    def play_game(self):
        secret = random.randint(1, 10)
        self.speak_text("Ich denke an eine Zahl zwischen 1 und 10. Rate!")
        guess = simpledialog.askinteger("Minispiel", "Welche Zahl denke ich?")
        if guess == secret:
            self.speak_text("Gewonnen!")
        else:
            self.speak_text(f"Falsch! Es war {secret}.")

    def trigger_jumpscare(self):
        self.is_busy = True
        self.speak_text("ACHTUNG ALARM!!!")
        orig_x, orig_y = self.root.winfo_x(), self.root.winfo_y()
        for _ in range(30):
            self.root.geometry(f"+{orig_x + random.randint(-40, 40)}+{orig_y + random.randint(-40, 40)}")
            time.sleep(0.04)
        self.root.geometry(f"+{orig_x}+{orig_y}")
        self.is_busy = False

    def delete_file_command(self):
        filename = simpledialog.askstring("Datei vernichten", "Welche Datei soll ich löschen?\n(z.B. test.txt)")
        if filename:
            threading.Thread(target=self.visual_search_and_destroy, args=(filename,), daemon=True).start()

    def visual_search_and_destroy(self, filename):
        self.is_busy = True
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        target_file = os.path.join(desktop_path, filename)
        onedrive_desktop = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop')
        
        if os.path.exists(target_file):
            final_path = target_file
        elif os.path.exists(os.path.join(onedrive_desktop, filename)):
            final_path = os.path.join(onedrive_desktop, filename)
        else:
            self.speak_text("Datei nicht gefunden.")
            self.is_busy = False
            return

        self.speak_text("Ich krieche zum Explorer!")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.crawl_to(int(sw / 2) - 75, sh - 200, speed_steps=80)
        time.sleep(0.5)
        
        self.speak_text(f"Und fresse {filename}!")
        self.crawl_to(int(sw / 2) - 75, int(sh / 2) - 75, speed_steps=80)
        
        try:
            os.remove(final_path)
            time.sleep(0.3)
            subprocess.Popen(f'explorer.exe /select,"{final_path}"')
            self.speak_text("Mampf! Weg.")
        except Exception:
            self.speak_text("Fehler beim Löschen.")
        self.is_busy = False

    def ask_ai_prompt(self, event=None):
        user_input = simpledialog.askstring("MazelBuddy Chat", "Stelle deiner Banane eine Frage:")
        if user_input:
            threading.Thread(target=self.get_ai_response, args=(user_input,), daemon=True).start()

    def get_ai_response(self, prompt):
        try:
            response = ollama.chat(model='llama3.2:1b', messages=[
                {'role': 'system', 'content': self.ai_personality},
                {'role': 'user', 'content': prompt}
            ])
            self.speak_text(response['message']['content'])
        except Exception:
            self.speak_text("Ollama schläft.")

    def random_movement_loop(self):
        while True:
            time.sleep(random.randint(15, 30))
            if self.is_busy: continue
            sw = self.root.winfo_screenwidth() - 200
            sh = self.root.winfo_screenheight() - 200
            self.crawl_to(random.randint(50, sw), random.randint(50, sh), speed_steps=50)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    buddy = DesktopBuddy()
    buddy.run()
