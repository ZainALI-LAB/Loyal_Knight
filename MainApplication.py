import tkinter as tk
from tkinter import messagebox
import hashlib
import json
import os
import sounddevice as sd
import wavio
import speech_recognition as sr
from monitor import LoyalKnightMonitor



import sys
import requests
import win32com.client

# ===== Auto-Start on Boot =====
def add_to_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_name = "LoyalKnight.lnk"
    shortcut_path = os.path.join(startup_folder, shortcut_name)
    target = sys.executable  # Path to your compiled .exe

    if not os.path.exists(shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.IconLocation = target
        shortcut.save()

# ===== Version Check =====
def check_for_update():
    try:
        remote_url = "https://raw.githubusercontent.com/YourUsername/loyalknight/main/latest_version.txt"
        remote_version = requests.get(remote_url, timeout=5).text.strip()

        if os.path.exists("version.txt"):
            with open("version.txt", "r") as f:
                local_version = f.read().strip()
        else:
            local_version = "0.0.0"

        if remote_version > local_version:
            messagebox.showinfo("Update Available", f"A new version ({remote_version}) is available.")
            # You could call a function like download_update() here
        else:
            print("You're up to date.")
    except Exception as e:
        print(f"Version check failed: {e}")

# ===== GUI App =====
def launch_main_gui():
    root = tk.Tk()
    root.title("Loyal Knight")
    root.geometry("400x300")
    label = tk.Label(root, text="Welcome to Loyal Knight!", font=("Arial", 16))
    label.pack(pady=100)
    root.mainloop()

# ===== Main Entry Point =====
if __name__ == "__main__":
    add_to_startup()
    check_for_update()
    launch_main_gui()




# --- Constants ---
PASSWORD_FILE = "config/password.json"
VOICE_PASSWORD_FILE = "config/voice_hash.txt"
SETTINGS_FILE = "config/user_settings.json"
FILENAME = "config/voice_sample.wav"
RECORD_SECONDS = 5
SAMPLE_RATE = 44100

# --- Utility Functions ---
def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def save_password(password):
    os.makedirs(os.path.dirname(PASSWORD_FILE), exist_ok=True)
    with open(PASSWORD_FILE, 'w') as f:
        json.dump({"password": hash_text(password)}, f)

def load_password():
    if not os.path.exists(PASSWORD_FILE):
        return ""
    with open(PASSWORD_FILE, 'r') as f:
        return json.load(f).get("password", "")

def verify_password(input_password):
    return hash_text(input_password) == load_password()

def record_voice():
    os.makedirs(os.path.dirname(VOICE_PASSWORD_FILE), exist_ok=True)
    print("[Voice] Recording...")
    audio_data = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    wavio.write(FILENAME, audio_data, SAMPLE_RATE, sampwidth=2)
    print("[Voice] Recording complete.")

def get_voice_text():
    r = sr.Recognizer()
    with sr.AudioFile(FILENAME) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except (sr.UnknownValueError, sr.RequestError):
        return None

def save_voice_password():
    record_voice()
    text = get_voice_text()
    if text:
        with open(VOICE_PASSWORD_FILE, "w") as f:
            f.write(hash_text(text))
        return True
    return False

def verify_voice_password():
    if not os.path.exists(VOICE_PASSWORD_FILE):
        return False
    record_voice()
    text = get_voice_text()
    if not text:
        return False
    with open(VOICE_PASSWORD_FILE, "r") as f:
        saved_hash = f.read().strip()
    return hash_text(text) == saved_hash

# --- GUI Application ---
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loyal Knight - Login")
        self.geometry("400x300")
        self.configure(bg="#1c1c1c")
        self.resizable(False, False)
        self.attempts = 0
        self.settings = {
            "internet_access": True,
            "use_voice_login": False,
            "features": {
                "malware_scan": True,
                "encryption": True,
                "decryption": True,
                "wake_timer": True
            }
        }
        self._login_screen()

    def _login_screen(self):
        tk.Label(self, text="Enter Password", font=("Segoe UI", 14), fg="white", bg="#1c1c1c").pack(pady=20)
        self.password_entry = tk.Entry(self, show="*", width=30)
        self.password_entry.pack()
        tk.Button(self, text="Login", command=self._login).pack(pady=10)
        tk.Button(self, text="Use Voice Recognition", command=self._voice_login).pack(pady=5)
        tk.Button(self, text="Change Password", command=self._change_password_prompt).pack(pady=10)

    def _login(self):
        password = self.password_entry.get()
        if verify_password(password):
            self._open_settings()
        else:
            self.attempts += 1
            if self.attempts >= 3:
                messagebox.showerror("Locked", "Too many failed attempts. Shutting down...")
                os.system("shutdown /s /t 1")
            else:
                messagebox.showerror("Error", f"Incorrect password. {3 - self.attempts} attempts left.")

    def _voice_login(self):
        if verify_voice_password():
            self._open_settings()
        else:
            messagebox.showerror("Error", "Voice verification failed.")

    def _change_password_prompt(self):
        top = tk.Toplevel(self)
        top.title("Change Password")
        top.geometry("300x200")
        tk.Label(top, text="Old Password:").pack()
        old_entry = tk.Entry(top, show="*")
        old_entry.pack()
        tk.Label(top, text="New Password:").pack()
        new_entry = tk.Entry(top, show="*")
        new_entry.pack()

        def update():
            if verify_password(old_entry.get()):
                save_password(new_entry.get())
                messagebox.showinfo("Success", "Password changed.")
                top.destroy()
            else:
                messagebox.showerror("Error", "Incorrect old password.")

        tk.Button(top, text="Change", command=update).pack(pady=10)

    def _open_settings(self):
        self.destroy()
        settings_app = SettingsWindow()
        settings_app.mainloop()


class SettingsWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loyal Knight Settings")
        self.geometry("700x500")
        self.configure(bg="#1c1c1c")
        self.resizable(False, False)
        self.settings = self.load_settings()
        self._create_widgets()
        
        self.monitor = LoyalKnightMonitor(self)
        self.monitor.start_monitoring()


    def _create_widgets(self):
        title = tk.Label(self, text="Loyal Knight Settings", font=("Segoe UI", 24), bg="#1c1c1c", fg="white")
        title.pack(pady=20)

        self.internet_var = tk.BooleanVar(value=self.settings["internet_access"])
        tk.Checkbutton(self, text="Allow Internet Access", variable=self.internet_var,
                       font=("Segoe UI", 14), bg="#1c1c1c", fg="white", selectcolor="#2a2a2a",
                       command=self.save_settings).pack(pady=10)

        self.voice_var = tk.BooleanVar(value=self.settings["use_voice_login"])
        tk.Checkbutton(self, text="Use Voice Recognition for Login", variable=self.voice_var,
                       font=("Segoe UI", 14), bg="#1c1c1c", fg="white", selectcolor="#2a2a2a",
                       command=self.save_settings).pack(pady=10)

        for feature in self.settings["features"]:
            var = tk.BooleanVar(value=self.settings["features"][feature])
            chk = tk.Checkbutton(self, text=f"Enable {feature.replace('_', ' ').title()}", variable=var,
                                 font=("Segoe UI", 13), bg="#1c1c1c", fg="white", selectcolor="#2a2a2a",
                                 command=lambda f=feature, v=var: self.toggle_feature(f, v))
            chk.pack(pady=5)

    def toggle_feature(self, feature, var):
        self.settings["features"][feature] = var.get()
        self.save_settings()

    def save_settings(self):
        self.settings["internet_access"] = self.internet_var.get()
        self.settings["use_voice_login"] = self.voice_var.get()
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        return {
            "internet_access": True,
            "use_voice_login": False,
            "features": {
                "malware_scan": True,
                "encryption": True,
                "decryption": True,
                "wake_timer": True
            }
        }

if __name__ == "__main__":
    if not os.path.exists(PASSWORD_FILE):
        save_password("admin")  # Default password on first run
    app = MainApplication()
    app.mainloop()

