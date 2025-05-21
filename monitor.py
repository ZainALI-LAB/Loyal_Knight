# monitor.py
import threading
import time
import os
import tkinter as tk

class LoyalKnightMonitor:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.running = False
        self.progress = 0

        # GUI Progress label
        self.progress_label = tk.Label(parent_frame, text="Scan Progress: 0%", font=("Segoe UI", 12), fg="white", bg="#1c1c1c")
        self.progress_label.pack(pady=10)

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.progress = 0
            threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        for i in range(101):  # Simulate 0% to 100%
            if not self.running:
                break
            self.progress = i
            time.sleep(0.1)  # Simulate scanning time
            self.update_progress()

    def update_progress(self):
        self.progress_label.config(text=f"Scan Progress: {self.progress}%")

    def stop_monitoring(self):
        self.running = False
