import os
import subprocess
import platform
import re
import psutil
import send2trash  

# ================= GLOBAL =================
current_file = None


# ================= DRIVE DETECTION =================
def get_all_drives():
    drives = []
    for partition in psutil.disk_partitions():
        try:
            if os.path.exists(partition.mountpoint):
                drives.append(partition.mountpoint)
        except:
            continue
    return drives


# ================= FILE SEARCH =================
def search_globally(filename):
    search_term = filename.lower().strip()
    drives = get_all_drives()

    print(f"Assistant: Searching for '{filename}'...")

    for drive in drives:
        try:
            for root, dirs, files in os.walk(drive, topdown=True):

                # Skip heavy/system folders
                dirs[:] = [d for d in dirs if d not in [
                    '$RECYCLE.BIN',
                    'System Volume Information',
                    'Windows',
                    'AppData',
                    'Program Files',
                    'Program Files (x86)',
                    'node_modules'
                ]]

                # 🔥 LIMIT DEPTH (IMPORTANT for speed)
                if root.count(os.sep) > 3:
                    continue

                for file in files:
                    if search_term in file.lower():
                        return os.path.join(root, file)

        except (PermissionError, OSError):
            continue

    return None


# ================= COMMAND PARSER =================
def parse_command(command):
    if not command:
        return ("none", [])

    command = command.lower().strip()
    command = command.replace(" dot ", ".")

    if "exit" in command or "stop" in command:
        return ("exit", [])

    for word in ["open", "search", "create", "delete"]:
        if command.startswith(word + " "):
            filename = command.replace(word + " ", "").strip()
            return (word, [filename])

    if "rename" in command and " to " in command:
        match = re.search(r"rename (.+?) to (.+)", command)
        if match:
            return ("rename", [match.group(1).strip(), match.group(2).strip()])

    return ("unknown", [])


# ================= MAIN HANDLER =================
def handle_file_command(command):
    action, params = parse_command(command)

    if action == "open" and params:
        path = search_globally(params[0])
        if path:
            try:
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", path])
                else:
                    subprocess.call(["xdg-open", path])

                return f"Opening {params[0]}"
            except Exception as e:
                return f"Error: {e}"

        return f"File '{params[0]}' not found"

    elif action == "search" and params:
        path = search_globally(params[0])
        return f"Found at {path}" if path else "File not found"

    elif action == "create" and params:
        try:
            with open(params[0], 'w') as f:
                pass
            return f"Created {params[0]}"
        except Exception as e:
            return f"Error: {e}"

    elif action == "rename" and len(params) == 2:
        path = search_globally(params[0])
        if path:
            new_path = os.path.join(os.path.dirname(path), params[1])
            os.rename(path, new_path)
            return f"Renamed to {params[1]}"

        return "Original file not found"

    elif action == "delete" and params:
        path = search_globally(params[0])
        if path:
            try:
                send2trash.send2trash(path)
                return f"{params[0]} moved to Recycle Bin"
            except Exception as e:
                return f"Error: {e}"

        return "File not found"

    return None