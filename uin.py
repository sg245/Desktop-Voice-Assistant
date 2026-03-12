# ================== IMPORTS ==================
import os
import subprocess
import datetime
import webbrowser
import threading
import math
import numpy as np
import pyaudio
import speech_recognition as sr
import tkinter as tk
import re
import pyttsx3
import pyautogui
import screen_brightness_control as sbc
from PIL import ImageGrab, Image, ImageTk
from cl import WindowsAssistant  # Your switch mode module

# ================== AUDIO CONFIG ==================
CHUNK = 1024
RATE = 44100
FORMAT = pyaudio.paInt16
CHANNELS = 1

# ================== MAIN CLASS ==================
class WindowsAssistantGUI:

    def __init__(self):
        self.running = True
        self.recognizer = sr.Recognizer()
        
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
            "take screenshot": self.take_screenshot,  # ✅ Fixed
            "what time is it": self.current_time,
            "what day is it": self.current_date,
            "shutdown": self.shutdown,
            "exit": self.exit_app
        }

        # ---------- WINDOW ----------
        self.root = tk.Tk()
        self.root.geometry("900x900")
        self.root.overrideredirect(True)
        self.root.configure(bg="black")

        # ---------- TITLE BAR ----------
        self.title_bar = tk.Frame(self.root, bg="#020617", height=35)
        self.title_bar.pack(fill="x")

        tk.Label(
            self.title_bar,
            text=" Windows Voice Assistant",
            bg="#020617",
            fg="white",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=10)

        tk.Button(
            self.title_bar,
            text="✕",
            bg="#020617",
            fg="white",
            bd=0,
            command=self.exit_app
        ).pack(side="right", padx=8)
        
        tk.Button(
            self.title_bar,
            text="—",
            bg="#020617",
            fg="white",
            bd=0,
            command=self.root.iconify
        ).pack(side="right", padx=5)

        
        self.title_bar.bind("<B1-Motion>", self.move_window)

        # ---------- CANVAS ----------
        self.canvas = tk.Canvas(
            self.root,
            width=900,
            height=865,
            highlightthickness=0,
            bd=0
        )
        self.canvas.place(x=0, y=35)

        # ---------- BACKGROUND ----------
        base_dir = os.path.dirname(__file__)
        bg_img = Image.open(os.path.join(base_dir, "gr.jpg")).resize((900, 865))
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        self.canvas.create_image(450, 432, image=self.bg_photo)

        self.text_id = self.canvas.create_text(
            450, 120,
            text="Speak a command...",
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

    # ================== WINDOW MOVE ==================
    def move_window(self, event):
        self.root.geometry(f"+{event.x_root}+{event.y_root}")

    # ================== SWITCH MODE ==================
    def open_switch_mode_window(self):
        self.root.withdraw()
        box = WindowsAssistant(self.root)
        box.root.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.root.deiconify()
        )

    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print("TTS error:", e)
    # ================== SYSTEM COMMANDS ==================
    def open_notepad(self):
        subprocess.Popen("notepad.exe")
        self.speak("Opening Notepad")
    def open_calculator(self):
        subprocess.Popen("calc.exe")
        self.speak("Opening calculator")
    def open_paint(self):
        try:
            subprocess.Popen("mspaint.exe")
            self.speak("Opening Paint")
            self.canvas.itemconfig(self.text_id, text="Opening Paint")
        except Exception as e:
            self.speak("Failed to open Paint")
            print(e)
    def open_camera(self):
        try:
            subprocess.Popen("start microsoft.windows.camera:", shell=True)
            self.speak("Opening Camera")
            self.canvas.itemconfig(self.text_id, text="Opening Camera")
        except Exception as e:
            self.speak("Unable to open camera")
            print(e)
    def open_browser(self):
        try:
            webbrowser.open("https://www.google.com")
            self.speak("Opening browser")
            self.canvas.itemconfig(self.text_id, text="Opening Browser")
        except Exception as e:
            self.speak("Unable to open browser")
            print(e)
    def open_cmd(self):
        try:
            subprocess.Popen("cmd.exe")
            self.speak("Opening command prompt")
            self.canvas.itemconfig(self.text_id, text="Opening Command Prompt")
        except Exception as e:
            self.speak("Failed to open command prompt")
            print(e)
    def open_explorer(self):
        try:
            subprocess.Popen("explorer.exe")
            self.speak("Opening file explorer")
            self.canvas.itemconfig(self.text_id, text="Opening File Explorer")
        except Exception as e:
            self.speak("Failed to open file explorer")
            print(e)

    # ================== SCREENSHOT ==================
    def take_screenshot(self):
        try:
            os.makedirs("screenshots", exist_ok=True)
            img = ImageGrab.grab()
            filename = f"screenshots/shot_{datetime.datetime.now():%H%M%S}.png"
            img.save(filename)

            self.canvas.itemconfig(self.text_id, text=f"Screenshot saved")

            self.speak("Screenshot captured")

        except Exception as e:
            self.speak("Screenshot failed")
            print("Screenshot error:", e)

    # ================== TIME / DATE ==================
    def current_time(self):
        now = datetime.datetime.now().strftime("%H:%M")
        self.canvas.itemconfig(self.text_id, text=f"Current Time: {now}")
        self.speak(f"The time is {now}")

    def current_date(self):
        try:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.canvas.itemconfig(self.text_id, text=f"Today's Date: {today}")
            self.speak(f"Today is {today}")
        except Exception as e:
            self.speak("Unable to get the date")
            print(e)

    # ================== SHUTDOWN ==================
    def shutdown(self):
        try:
            self.speak("Shutting down the system in five seconds")
            self.canvas.itemconfig(self.text_id, text="Shutting down system")
            os.system("shutdown /s /t 5")
        except Exception as e:
            self.speak("Shutdown failed")
            print(e)

    # ================== BRIGHTNESS ==================
    def control_brightness(self, command):
        try:
            current = sbc.get_brightness()[0]

            if "increase brightness" in command or "brightness up" in command:
                sbc.set_brightness(min(current + 10, 100))
                self.speak("Increasing brightness")

            elif "decrease brightness" in command or "brightness down" in command:
                sbc.set_brightness(max(current - 10, 0))
                self.speak("Decreasing brightness")

            elif "set brightness to" in command:
                match = re.search(r'\d+', command)
                if match:
                    value = max(0, min(int(match.group()), 100))
                    sbc.set_brightness(value)
                    self.speak(f"Setting brightness to {value} percent")

        except Exception as e:
            self.speak("Brightness control failed")
            print("Brightness error:", e)

    # ================== VOLUME ==================
    def control_volume(self, command):

        if "volume up" in command or "increase volume" in command:
            pyautogui.press("volumeup")
            self.speak("Increasing volume")

        elif "volume down" in command or "decrease volume" in command:
            pyautogui.press("volumedown")
            self.speak("Decreasing volume")

        elif "mute" in command:
            pyautogui.press("volumemute")
            self.speak("Muting volume")

    
    # ================== VOICE ==================
    def listen_command(self):
        try:
            with sr.Microphone() as src:
                print("Listening...")
                audio = self.recognizer.listen(src)  # Just listen, no noise adjustment
                cmd = self.recognizer.recognize_google(audio).lower()  # Convert to text
                self.canvas.itemconfig(self.text_id, text=cmd)
                print("Heard:", cmd)
                return cmd
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Google API error: {e}")
            return ""
        except Exception as e:
            print("Voice recognition error:", e)
            return ""




    def command_loop(self):
        while self.running:
            cmd = self.listen_command()  # Get recognized voice

            # Control brightness and volume
            self.control_brightness(cmd)
            self.control_volume(cmd)

            # Check commands with startswith for flexibility
            for key in self.commands:
                if cmd.startswith(key):
                    # Run command safely in main thread
                    self.root.after(0, self.commands[key])
                    break


    # ================== WAVE ==================
    def update_wave(self):
        #if not self.running:
        #    return

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

            self.canvas.create_line(
                points,
                fill="white",
                width=width,
                smooth=True,
                tags="wave"
            )

        self.phase += 0.1
        self.root.after(30, self.update_wave)

    # ================== EXIT ==================
    def exit_app(self):
        self.running = False
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        except:
            pass
        self.root.destroy()

    # ================== RUN ==================
    def run(self):
        self.speak("Assistant ready. Waiting for your command.")
        threading.Thread(target=self.command_loop, daemon=True).start()
        self.update_wave()
        self.root.mainloop()


# ================== START ==================
if __name__ == "__main__":
    WindowsAssistantGUI().run()
