import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image
from db import get_current_user, logout_current_user
from l import open_login
from uin import WindowsAssistantGUI

# ================= GLOBAL STATE =================
assistant_thread = None
assistant_instance = None


# ================= ASSISTANT CONTROL =================
def start_assistant():
    global assistant_instance
    assistant_instance = WindowsAssistantGUI()
    assistant_instance.run()

def stop_assistant():
    global assistant_instance
    if assistant_instance:
        try:
            assistant_instance.exit_app()
        except:
            pass
        assistant_instance = None


# ================= TRAY CALLBACKS =================
def on_login(icon, item):
    import subprocess
    subprocess.Popen(["python", "l.py"])


def on_logout(icon, item):
    import threading
    import ctypes
    import subprocess

    def logout_flow():
        result = ctypes.windll.user32.MessageBoxW(
            0,
            "User will be logged out.\nDo you want to continue?",
            "Logout",
            4 | 32  # YES/NO + Warning icon
        )

        if result == 6:  # YES
            logout_current_user()
            stop_assistant()

            subprocess.Popen(["python", "l.py"])

    # ✅ Run popup in separate thread (prevents tray freeze)
    threading.Thread(target=logout_flow, daemon=True).start()
        
def on_exit(icon, item):
    stop_assistant()
    icon.stop()
# ================= TRAY START =================
def start_tray():
    global assistant_thread

    # Start assistant automatically if user already logged in
    if get_current_user():
        assistant_thread = threading.Thread(
            target=start_assistant,daemon=True
        )
        assistant_thread.start()

    # ===== LOAD PNG ICON SAFELY =====
    image = Image.open("icon.png").convert("RGBA")
    image = image.resize((64, 64), Image.LANCZOS)  # best size for tray

    menu = Menu(
        MenuItem("Login", on_login),
        MenuItem("Logout", on_logout),
        MenuItem("Exit", on_exit)
    )

    icon = Icon(
        "Jarvis",
        image,
        "Jarvis Assistant",
        menu
    )

    icon.run()


# ================= ENTRY =================
if __name__ == "__main__":
    from db import init_db
    init_db()
    start_tray()
