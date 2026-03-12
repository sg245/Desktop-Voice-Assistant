# main.py (simplified, correct role)
from db import init_db
from stray import start_tray

if __name__ == "__main__":
    init_db()
    start_tray()
