import os
import sys
import shutil
import win32com.client

def add_to_startup():
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    script_path = os.path.abspath(sys.argv[0])
    shortcut_path = os.path.join(startup_folder, "LoyalKnight.lnk")

    if not os.path.exists(shortcut_path):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.Save()
        return True
    return False

def remove_from_startup():
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    shortcut_path = os.path.join(startup_folder, "LoyalKnight.lnk")
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        return True
    return False

def is_in_startup():
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    shortcut_path = os.path.join(startup_folder, "LoyalKnight.lnk")
    return os.path.exists(shortcut_path)
