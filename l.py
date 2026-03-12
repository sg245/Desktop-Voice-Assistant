import threading
import tkinter as tk
from tkinter import messagebox
# Removed old assistant imports to use the new GUI from uin.py
from db import set_current_user, validate_user, add_user, init_db, logout_current_user
from uin import WindowsAssistantGUI  # Import the new GUI class
import re
def is_valid_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, ""

def open_login():
    init_db()
    root = tk.Tk()
    root.title("Login")
    root.geometry("360x460")
    root.configure(bg="#f0f2f5")
    root.resizable(False, False)

    # Title
    tk.Label(
        root,
        text="Desktop Assistant",
        font=("Helvetica", 16, "bold"),
        bg="#f0f2f5",
        fg="#333"
    ).pack(pady=(20, 15))

    # Content Frame
    content = tk.Frame(root, bg="#f0f2f5", width=280)
    content.pack(padx=40)

    # Username
    tk.Label(content, text="Username", bg="#f0f2f5").pack(anchor="w")
    username_entry = tk.Entry(content)
    username_entry.pack(fill="x", pady=(2, 10), ipady=4)

    # Password
    tk.Label(content, text="Password", bg="#f0f2f5").pack(anchor="w")
    password_entry = tk.Entry(content, show="*")
    password_entry.pack(fill="x", pady=(2, 10), ipady=4)

    # Options Frame
    options = tk.Frame(content, bg="#f0f2f5")
    options.pack(fill="x", pady=(0, 15))

    # Show/Hide Password
    def toggle_password():
        if password_entry.cget("show") == "*":
            password_entry.config(show="")
            show_btn.config(text="Hide Password")
        else:
            password_entry.config(show="*")
            show_btn.config(text="Show Password")

    show_btn = tk.Button(
        options,
        text="Show Password",
        relief="flat",
        bg="#f0f2f5",
        fg="#4a90e2",
        cursor="hand2",
        command=toggle_password
    )
    show_btn.pack(side="left")

    # Forgot Password (UI only)
    def forgot_password():
        fp_window = tk.Toplevel(root)
        fp_window.title("Reset Password")
        fp_window.geometry("300x250")
        fp_window.configure(bg="#f0f2f5")
        fp_window.resizable(False, False)

        tk.Label(fp_window, text="Reset Your Password", font=("Helvetica", 14, "bold"), bg="#f0f2f5").pack(pady=15)
        tk.Label(fp_window, text="New Password", bg="#f0f2f5").pack(anchor="w", padx=20)
        new_pass_entry = tk.Entry(fp_window, show="*")
        new_pass_entry.pack(fill="x", padx=20, pady=(2, 10), ipady=4)
        tk.Label(fp_window, text="Confirm Password", bg="#f0f2f5").pack(anchor="w", padx=20)
        confirm_pass_entry = tk.Entry(fp_window, show="*")
        confirm_pass_entry.pack(fill="x", padx=20, pady=(2, 10), ipady=4)

        def save_password():
            new_pass = new_pass_entry.get().strip()
            confirm_pass = confirm_pass_entry.get().strip()

            if not new_pass or not confirm_pass:
                messagebox.showerror("Error", "Fields cannot be empty")
                return

            if new_pass != confirm_pass:
                messagebox.showerror("Error", "Passwords do not match")
                return

            valid, msg = is_valid_password(new_pass)
            if not valid:
                messagebox.showerror("Invalid Password", msg)
                return

            messagebox.showinfo("Success", "Password set successfully!")
            fp_window.destroy()


        tk.Button(
            fp_window,
            text="Save",
            bg="#4a90e2",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            command=save_password
        ).pack(fill="x", padx=20, ipady=6, pady=15)

    tk.Button(
        options,
        text="Forgot Password?",
        relief="flat",
        bg="#f0f2f5",
        fg="#e74c3c",
        cursor="hand2",
        command=forgot_password
    ).pack(side="right")

    # Register Function
    def register():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Fields cannot be empty")
            return

        valid, msg = is_valid_password(password)
        if not valid:
            messagebox.showerror("Invalid Password", msg)
            return

        if add_user(username, password):
            messagebox.showinfo("Success", "Registered successfully!")
        else:
            messagebox.showerror("Error", "Username already exists!")

    # Login Function
    def login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Fields cannot be empty")
            return
            
        if validate_user(username, password):
            set_current_user(username)
            messagebox.showinfo("Success", "Login successful")
            
            # 1. Close the login window
            root.destroy()

            # 2. Launch the WindowsAssistantGUI from uin.py immediately
            assistant_gui = WindowsAssistantGUI()
            assistant_gui.run()
            
        else:
            messagebox.showerror("Error", "Invalid username or password")

    # Buttons
    tk.Button(
        content,
        text="Register",
        bg="#2ecc71",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        command=register
    ).pack(fill="x", ipady=6, pady=(0, 10))

    tk.Button(
        content,
        text="Login",
        bg="#4a90e2",
        fg="white",
        font=("Arial", 10, "bold"),
        relief="flat",
        command=login
    ).pack(fill="x", ipady=6)

    # Footer
    tk.Label(
        root,
        text="Jarvis Assistant",
        font=("Arial", 8),
        bg="#f0f2f5",
        fg="#555"
    ).pack(side="bottom", pady=8)

    def on_close():
        logout_current_user()
        root.destroy()

    root.mainloop()
    
if __name__ == "__main__":
    open_login()