"""
Login gate for the whole app. Only an admin with valid credentials can get
into the Dashboard. A "Submit a Complaint" option is also available here,
without logging in, for anyone (hospital staff, cleaning crew, etc.) who
wants to report a problem.
"""

import hashlib
import tkinter as tk
from tkinter import ttk, messagebox

from dao.admin_dao import AdminDAO
from dao.complaint_dao import ComplaintDAO
from models.complaint import Complaint
from utils.validators import is_non_empty_string


class LoginWindow(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Biomedical Waste Robot - Admin Login")
        self.geometry("420x420")
        self.configure(bg="#f4f6f8")
        self.resizable(False, False)

        self.admin_dao = AdminDAO()
        self.authenticated = False

        self._build()

    def _build(self):
        tk.Label(
            self, text="Biomedical Waste Robot",
            font=("Segoe UI", 16, "bold"), bg="#f4f6f8", fg="#1b3a4b",
        ).pack(pady=(30, 4))
        tk.Label(
            self, text="Admin Login", font=("Segoe UI", 11), bg="#f4f6f8", fg="#555",
        ).pack(pady=(0, 20))

        form = tk.Frame(self, bg="#f4f6f8")
        form.pack()

        tk.Label(form, text="Username", bg="#f4f6f8").grid(row=0, column=0, sticky="w", pady=6)
        self.username_var = tk.StringVar()
        tk.Entry(form, textvariable=self.username_var, width=26).grid(row=0, column=1, pady=6)

        tk.Label(form, text="Password", bg="#f4f6f8").grid(row=1, column=0, sticky="w", pady=6)
        self.password_var = tk.StringVar()
        tk.Entry(form, textvariable=self.password_var, show="*", width=26).grid(row=1, column=1, pady=6)

        tk.Button(
            self, text="Login", command=self._attempt_login,
            bg="#2f7a63", fg="white", relief="flat", width=18, height=1,
        ).pack(pady=20)
        self.bind("<Return>", lambda e: self._attempt_login())

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=30, pady=10)

        tk.Label(
            self, text="Not an admin? You can still report a problem:",
            bg="#f4f6f8", fg="#555", font=("Segoe UI", 9),
        ).pack()
        tk.Button(
            self, text="Submit a Complaint", command=self._open_complaint_form,
            bg="#3a6ea5", fg="white", relief="flat", width=22,
        ).pack(pady=12)

    def _attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("Missing info", "Enter both username and password.")
            return

        admin = self.admin_dao.get_by_username(username)
        if admin is None:
            messagebox.showerror("Login failed", "No such admin user.")
            return

        # NOTE: MD5 matches the seed data for this demo only.
        # Swap for a real password hashing scheme (e.g. bcrypt) before real use.
        hashed = hashlib.md5(password.encode()).hexdigest()
        if hashed != admin.password_hash:
            messagebox.showerror("Login failed", "Incorrect password.")
            return

        self.authenticated = True
        self.destroy()

    def _open_complaint_form(self):
        ComplaintFormWindow(self)


class ComplaintFormWindow(tk.Toplevel):
    """Open to anyone - no login required. Anonymous complaints are allowed."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Submit a Complaint")
        self.geometry("380x360")
        self.complaint_dao = ComplaintDAO()

        tk.Label(self, text="Report a Problem", font=("Segoe UI", 13, "bold")).pack(pady=12)
        tk.Label(
            self, text="Name and contact are optional - you may submit anonymously.",
            fg="#666", wraplength=320, justify="left",
        ).pack(padx=20)

        form = tk.Frame(self)
        form.pack(fill="x", padx=20, pady=10)

        tk.Label(form, text="Name (optional):").grid(row=0, column=0, sticky="w", pady=6)
        self.name_var = tk.StringVar()
        tk.Entry(form, textvariable=self.name_var, width=28).grid(row=0, column=1, pady=6)

        tk.Label(form, text="Contact (optional):").grid(row=1, column=0, sticky="w", pady=6)
        self.contact_var = tk.StringVar()
        tk.Entry(form, textvariable=self.contact_var, width=28).grid(row=1, column=1, pady=6)

        tk.Label(self, text="Complaint / Issue:").pack(anchor="w", padx=20)
        self.message_text = tk.Text(self, height=6, width=40, wrap="word")
        self.message_text.pack(padx=20, pady=6)

        self.status_label = tk.Label(self, text="", fg="#333")
        self.status_label.pack()

        tk.Button(
            self, text="Submit Complaint", command=self._submit,
            bg="#2f7a63", fg="white", relief="flat", width=18,
        ).pack(pady=10)

    def _submit(self):
        message = self.message_text.get("1.0", "end").strip()
        if not is_non_empty_string(message):
            messagebox.showwarning("Missing info", "Please describe the issue before submitting.")
            return

        self.complaint_dao.create(Complaint(
            complaint_id=None,
            message=message,
            name=self.name_var.get().strip(),
            contact=self.contact_var.get().strip(),
        ))
        messagebox.showinfo("Thank you", "Your complaint has been submitted.")
        self.destroy()
