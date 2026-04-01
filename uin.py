# ================== IMPORTS ==================
import os
import subprocess
import datetime
import webbrowser
import threading
import time
import math
import numpy as np
import pyaudio
import speech_recognition as sr
import tkinter as tk
import pyautogui
import screen_brightness_control as sbc
import pyttsx3
from PIL import ImageGrab, Image, ImageTk
from cl import WindowsAssistant
from tkinter import messagebox
from db import logout_current_user
from file_ops import handle_file_command

# ================== AUDIO CONFIG ==================
CHUNK = 1024
RATE = 44100
FORMAT = pyaudio.paInt16
CHANNELS = 1


# ================== MAIN CLASS ==================
class WindowsAssistantGUI:

    def __init__(self, on_logout=None):
        self.on_logout = on_logout
        self.running = True
        self.active_mode = False
        self.recognizer = sr.Recognizer()

        # ---------- WINDOW ----------
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.overrideredirect()
        self.root.configure(bg="black")
        self.root.withdraw()  # start hidden

        # ---------- TTS ----------
        self.engine = pyttsx3.init("sapi5")
        self.engine.setProperty("rate", 175)
        self.engine.setProperty("volume", 1.0)

        # ---------- AUDIO ----------
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        # ---------- COMMANDS ----------
        self.commands = {
            "open notepad": self.open_notepad,
            "open calculator": self.open_calculator,
            "open calc": self.open_calculator,
            "open paint": self.open_paint,
            "open camera": self.open_camera,
            "open browser": self.open_browser,
            "open command prompt": self.open_cmd,
            "open file explorer": self.open_explorer,
            "take screenshot": self.take_screenshot,
            "what time is it": self.current_time,
            "what day is it": self.current_date,
            "shutdown": self.shutdown
        }

        # ---------- TITLE BAR ----------
        self.title_bar = tk.Frame(self.root, bg="#020617", height=35)
        self.title_bar.pack(fill="x")

        tk.Label(self.title_bar, text=" Windows Voice Assistant",
                 bg="#020617", fg="white",
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

        tk.Button(self.title_bar, text="✕",
                  bg="#020617", fg="white", bd=0,
                  command=self.exit_app).pack(side="right", padx=8)

        tk.Button(self.title_bar, text="—",
                  bg="#020617", fg="white", bd=0,
                  command=self.root.iconify).pack(side="right", padx=5)

        self.title_bar.bind("<B1-Motion>", self.move_window)

        # ---------- CANVAS ----------
        self.canvas = tk.Canvas(self.root, width=900, height=865,
                                highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=35)

        base_dir = os.path.dirname(__file__)
        bg_img = Image.open(os.path.join(base_dir, "gr.jpg")).resize((900, 865))
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        self.canvas.create_image(450, 432, image=self.bg_photo)

        self.text_id = self.canvas.create_text(
            450, 120,
            text="Waiting for wake word...",
            fill="white",
            font=("Segoe UI Semibold", 18),
            width=520
        )

        self.switch_btn = tk.Button(
            self.root,
            text="Switch Mode",
            bg="#0f172a",
            fg="white",
            width=14,
            command=self.open_switch_mode_window
        )
        self.switch_btn.place(x=450, y=800, anchor="center")

        self.phase = 0

    # ================== TTS ==================
    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)

    # ================== WINDOW ==================
    def move_window(self, event):
        self.root.geometry(f"+{event.x_root}+{event.y_root}")

    def show_window(self):
        def _show():
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.update()
            self.root.attributes('-topmost', False)

        self.root.after(0, _show)

    def open_switch_mode_window(self):
        self.root.withdraw()
        box = WindowsAssistant(self.root)
        box.root.protocol("WM_DELETE_WINDOW",
                          lambda: self.root.deiconify())

    # ================== COMMAND PROCESS ==================
    def process_command(self, cmd):
        # ================= FILE OPERATIONS =================
        file_result = handle_file_command(cmd)

        if file_result:
            print(f"Assistant: {file_result}")
            self.canvas.itemconfig(self.text_id, text=file_result)
            return
        self.control_brightness(cmd)
        self.control_volume(cmd)

        # SMART HANDLING
        if "time" in cmd:
            self.root.after(0, self.current_time)
            return

        if "date" in cmd or "day" in cmd:
            self.root.after(0, self.current_date)
            return

        for key in self.commands:
            if key in cmd:
                self.root.after(0, self.commands[key])
                return

        self.speak("Sorry, I did not understand")

    # ================== SYSTEM COMMANDS ==================
    def open_notepad(self):
        subprocess.Popen("notepad.exe")
        self.speak("Opening Notepad")

    def open_calculator(self):
        subprocess.Popen("calc.exe")
        self.speak("Opening Calculator")

    def open_paint(self):
        subprocess.Popen("mspaint.exe")
        self.speak("Opening Paint")

    def open_camera(self):
        subprocess.Popen("start microsoft.windows.camera:", shell=True)
        self.speak("Opening Camera")

    def open_browser(self):
        webbrowser.open("https://www.google.com")
        self.speak("Opening Browser")

    def open_cmd(self):
        subprocess.Popen("cmd.exe")
        self.speak("Opening Command Prompt")

    def open_explorer(self):
        subprocess.Popen("explorer.exe")
        self.speak("Opening File Explorer")

    # ================== SCREENSHOT ==================
    def take_screenshot(self):
        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/shot_{datetime.datetime.now():%H%M%S}.png"
        ImageGrab.grab().save(filename)
        self.speak("Screenshot captured")

    # ================== TIME ==================
    def current_time(self):
        now = datetime.datetime.now().strftime("%H:%M")
        self.speak(f"The time is {now}")

    def current_date(self):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self.speak(f"Today is {today}")

    # ================== SHUTDOWN ==================
    def shutdown(self):
        self.speak("Shutting down system")
        os.system("shutdown /s /t 5")

    # ================== BRIGHTNESS ==================
    def control_brightness(self, cmd):
        try:
            current = sbc.get_brightness()[0]

            if "increase brightness" in cmd:
                sbc.set_brightness(min(current + 10, 100))
                self.speak("Increasing brightness")

            elif "decrease brightness" in cmd:
                sbc.set_brightness(max(current - 10, 0))
                self.speak("Decreasing brightness")

        except:
            pass

    # ================== VOLUME ==================
    def control_volume(self, cmd):
        if "volume up" in cmd:
            pyautogui.press("volumeup")
            self.speak("Volume up")

        elif "volume down" in cmd:
            pyautogui.press("volumedown")
            self.speak("Volume down")

        elif "mute" in cmd:
            pyautogui.press("volumemute")
            self.speak("Muted")

    
    # ================== VOICE ==================
    def listen_command(self):
        try:
            with sr.Microphone() as src:
                audio = self.recognizer.listen(src)
                return self.recognizer.recognize_google(audio).lower()
        except:
            return ""

    # ================== WAKE WORD ==================
    def wake_word_listener(self):
        wake_words = ["jarvis", "hey jarvis", "wake up", "hello jarvis", "activate"]

        with sr.Microphone() as src:
            self.recognizer.adjust_for_ambient_noise(src)

            while self.running:
                try:
                    if self.active_mode:
                        time.sleep(0.5)
                        continue

                    audio = self.recognizer.listen(src, timeout=5, phrase_time_limit=3)
                    phrase = self.recognizer.recognize_google(audio).lower()

                    if any(w in phrase for w in wake_words):
                        print("Wake word detected!")

                        self.active_mode = True
                        self.speak("Yes?")
                        self.show_window()

                        self.root.after(0, lambda:
                            self.canvas.itemconfig(self.text_id,
                                                   text="Listening...")
                        )

                        threading.Thread(
                            target=self.active_command_loop,
                            daemon=True
                        ).start()

                except:
                    continue

    # ================== ACTIVE SESSION ==================
    def active_command_loop(self):
        while self.active_mode and self.running:
            cmd = self.listen_command()

            if not cmd:
                continue

            print("Command:", cmd)

            if "exit" in cmd or "go to sleep" in cmd:
                self.speak("Going to sleep")
                self.active_mode = False

                self.root.after(0, self.root.withdraw)

                self.root.after(0, lambda:
                    self.canvas.itemconfig(self.text_id,
                                           text="Waiting for wake word...")
                )
                break

            self.process_command(cmd)

    # ================== WAVE ==================
    def update_wave(self):
        try:
            data = np.frombuffer(
                self.stream.read(CHUNK, exception_on_overflow=False),
                dtype=np.int16
            )
            volume = min(np.linalg.norm(data) / 3000, 1.5)
        except:
            volume = 0.5

        self.canvas.delete("wave")

        cx, cy = 450, 430
        base_radius = 90
        max_amp = 25
        angle_step = 0.07

        for width, shift in [(2, 0), (3, 40), (4, 80)]:
            points = []
            for i in range(int(2 * math.pi / angle_step)):
                angle = i * angle_step
                deform = volume * max_amp * math.sin(angle * 3 + self.phase + shift)
                r = base_radius + deform
                points.extend([
                    cx + r * math.cos(angle),
                    cy + r * math.sin(angle)
                ])

            self.canvas.create_line(points, fill="white",
                                    width=width, smooth=True, tags="wave")

        self.phase += 0.1
        self.root.after(30, self.update_wave)

    # ================== EXIT ==================
    def exit_app(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.root.destroy()

    # ================== RUN ==================
    def run(self):
        self.speak("Assistant ready")
        threading.Thread(target=self.wake_word_listener, daemon=True).start()
        self.update_wave()
        self.root.mainloop()


# ================== START ==================
if __name__ == "__main__":
    WindowsAssistantGUI().run()