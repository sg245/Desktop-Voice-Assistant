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
    assistant = WindowsAssistantGUI()
    assistant.run()


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
    # Open login window safely (do NOT block tray)
    threading.Thread(target=open_login, daemon=True).start()


def on_logout(icon, item):
    logout_current_user()
    stop_assistant()


def on_exit(icon, item):
    stop_assistant()
    icon.stop()   # ✅ ONLY PLACE icon.stop() IS USED


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
