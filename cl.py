import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import webbrowser
import datetime
import os
from PIL import ImageGrab

class WindowsAssistant:
    def __init__(self, parent):
        # Create Toplevel window
        self.root = tk.Toplevel(parent)
        self.root.title("Windows Assistant")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # ---------- TITLE ----------
        tk.Label(
            self.root,
            text="Windows Assistant",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        # ---------- STATUS LABEL ----------
        self.status_label = tk.Label(
            self.root,
            text="Ready for commands",
            bg="#ecf0f1",
            relief="solid",
            height=2
        )
        self.status_label.pack(fill="x", padx=20, pady=5)

        # ---------- COMMAND HISTORY ----------
        tk.Label(
            self.root,
            text="Command History",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.history_text = scrolledtext.ScrolledText(
            self.root,
            height=6,
            state="disabled"
        )
        self.history_text.pack(fill="x", padx=20)

        # ---------- BUTTONS ----------
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Left column
        left = tk.Frame(frame)
        left.pack(side="left", padx=10)
        tk.Button(left, text="Open Notepad", width=20, command=self.open_notepad).pack(pady=3)
        tk.Button(left, text="Open Calculator", width=20, command=self.open_calculator).pack(pady=3)
        tk.Button(left, text="Open Browser", width=20, command=self.open_browser).pack(pady=3)
        tk.Button(left, text="Take Screenshot", width=20, command=self.take_screenshot).pack(pady=3)

        # Right column
        right = tk.Frame(frame)
        right.pack(side="right", padx=10)
        tk.Button(right, text="Open Paint", width=20, command=self.open_paint).pack(pady=3)
        tk.Button(right, text="Open CMD", width=20, command=self.open_cmd).pack(pady=3)
        tk.Button(right, text="Open Explorer", width=20, command=self.open_explorer).pack(pady=3)
        tk.Button(right, text="Current Time", width=20, command=self.current_time).pack(pady=3)
        tk.Button(right, text="Current Date", width=20, command=self.current_date).pack(pady=3)

        # Exit button
        tk.Button(
            self.root,
            text="Exit",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.exit_app
        ).pack(pady=20)

    # ---------- LOGGING ----------
    def log(self, text):
        self.history_text.config(state="normal")
        t = datetime.datetime.now().strftime("%H:%M:%S")
        self.history_text.insert("end", f"{t}: {text}\n")
        self.history_text.config(state="disabled")
        self.history_text.see("end")
        self.status_label.config(text=text)

    # ---------- SYSTEM COMMANDS ----------
    def open_notepad(self):
        subprocess.Popen("notepad")
        self.log("Opened Notepad")

    def open_calculator(self):
        subprocess.Popen("calc")
        self.log("Opened Calculator")

    def open_paint(self):
        subprocess.Popen("mspaint")
        self.log("Opened Paint")

    def open_browser(self):
        webbrowser.open("https://www.google.com")
        self.log("Opened Browser")

    def open_cmd(self):
        subprocess.Popen("cmd")
        self.log("Opened Command Prompt")

    def open_explorer(self):
        subprocess.Popen("explorer")
        self.log("Opened File Explorer")

    def take_screenshot(self):
        try:
            os.makedirs("screenshots", exist_ok=True)
            filename = f"screenshots/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            ImageGrab.grab().save(filename)
            self.log(f"Screenshot saved: {filename}")
        except Exception as e:
            self.log(f"Screenshot failed: {e}")

    def current_time(self):
        now = datetime.datetime.now().strftime("%I:%M %p")
        self.log(f"Current Time: {now}")

    def current_date(self):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self.log(f"Current Date: {today}")

    def shutdown(self):
        if messagebox.askyesno("Shutdown", "Shutdown system now?"):
            os.system("shutdown /s /t 0")

    def exit_app(self):
        self.root.destroy()
