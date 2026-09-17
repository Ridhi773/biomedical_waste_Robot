"""QR Verification Log - read-only audit trail of every pickup/destination scan."""

import tkinter as tk
from tkinter import ttk

from services.qr_service import QRService

RESULT_COLORS = {"match": "#eaf5e9", "mismatch": "#fde3e3"}


class QRVerificationLogWindow(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("QR Verification Log")
        self.geometry("640x420")
        self.qr_service = QRService()

        tk.Label(self, text="QR Verification Log", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("transport", "robot", "stage", "scanned", "expected", "result", "time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        headings = {
            "transport": "Transport", "robot": "Robot", "stage": "Stage",
            "scanned": "Scanned Code", "expected": "Expected Code",
            "result": "Result", "time": "Verified At",
        }
        widths = {"transport": 70, "robot": 70, "stage": 80, "scanned": 100,
                  "expected": 100, "result": 80, "time": 130}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for result, color in RESULT_COLORS.items():
            self.tree.tag_configure(result, background=color)

        tk.Button(self, text="Refresh", command=self.load_data, bg="#2f7a63", fg="white",
                  relief="flat").pack(pady=(0, 10))

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.qr_service.list_log():
            self.tree.insert("", "end", values=(
                row["transport_id"], row["robot_name"], row["stage"].title(),
                row["scanned_code"], row["expected_code"], row["result"].title(),
                str(row["verified_at"]),
            ), tags=(row["result"],))
