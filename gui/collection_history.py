"""Collection History screen — table of past waste collections, newest first."""

import tkinter as tk
from tkinter import ttk

from services.collection_service import CollectionService


class CollectionHistoryWindow(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Collection History")
        self.geometry("620x400")
        self.collection_service = CollectionService()

        tk.Label(self, text="Collection History", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("robot", "waste", "category", "weight", "location", "collected_at")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=14)
        headings = {
            "robot": "Robot", "waste": "Waste Type", "category": "Category",
            "weight": "Weight (kg)", "location": "Location", "collected_at": "Collected At",
        }
        widths = {"robot": 70, "waste": 130, "category": 90, "weight": 80, "location": 120, "collected_at": 130}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(self, text="Refresh", command=self.load_data, bg="#2f7a63", fg="white",
                  relief="flat").pack(pady=(0, 10))

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.collection_service.list_with_details():
            self.tree.insert("", "end", values=(
                row["robot_name"], row["waste_name"], row["waste_category"].title(),
                f"{row['weight_kg']:.2f}", row["location_name"] or "-", str(row["collected_at"]),
            ))
