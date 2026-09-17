"""Complaints screen (admin-only) - view complaints submitted from the login page."""

import tkinter as tk
from tkinter import ttk, messagebox

from dao.complaint_dao import ComplaintDAO


class ComplaintsWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Complaints")
        self.geometry("620x420")
        self.on_change = on_change
        self.complaint_dao = ComplaintDAO()

        tk.Label(self, text="Submitted Complaints", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("name", "contact", "message", "status", "created")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        headings = {
            "name": "Name", "contact": "Contact", "message": "Message",
            "status": "Status", "created": "Submitted",
        }
        widths = {"name": 100, "contact": 100, "message": 230, "status": 70, "created": 120}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w" if col == "message" else "center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.tag_configure("open", background="#fff6db")
        self.tree.tag_configure("resolved", background="#eaf5e9")

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Mark Resolved", command=self.resolve_selected,
                  bg="#2f7a63", fg="white", relief="flat", width=16).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Refresh", command=self.load_data,
                  bg="#e0e0e0", relief="flat", width=10).grid(row=0, column=1, padx=6)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for c in self.complaint_dao.get_all():
            self.tree.insert("", "end", iid=str(c.complaint_id), values=(
                c.name or "Anonymous", c.contact or "-", c.message,
                c.status.title(), c.created_at,
            ), tags=(c.status,))

    def resolve_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select a complaint to mark resolved.")
            return
        self.complaint_dao.resolve(int(selected[0]))
        self.load_data()
        if self.on_change:
            self.on_change()
