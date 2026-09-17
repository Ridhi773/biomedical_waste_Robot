"""Alerts screen — lists active/resolved alerts, lets you resolve them or simulate a new one."""

import tkinter as tk
from tkinter import ttk, messagebox

from dao.alert_dao import AlertDAO
from services.robot_service import RobotService
from services.simulation_service import SimulationService

SEVERITY_COLORS = {"low": "#eaf5e9", "medium": "#fff6db", "high": "#fde3e3", "critical": "#f8caca"}


class AlertsWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Alerts")
        self.geometry("620x440")
        self.on_change = on_change

        self.alert_dao = AlertDAO()
        self.robot_service = RobotService()
        self.simulation_service = SimulationService()

        tk.Label(self, text="Robot Alerts", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("robot", "type", "severity", "message", "created", "resolved")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        headings = {
            "robot": "Robot", "type": "Type", "severity": "Severity",
            "message": "Message", "created": "Created", "resolved": "Resolved",
        }
        widths = {"robot": 70, "type": 100, "severity": 70, "message": 200, "created": 120, "resolved": 70}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w" if col == "message" else "center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for sev, color in SEVERITY_COLORS.items():
            self.tree.tag_configure(sev, background=color)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Resolve Selected", command=self.resolve_selected,
                  bg="#2f7a63", fg="white", relief="flat", width=16).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Simulate Random Event", command=self.simulate_event,
                  bg="#3a6ea5", fg="white", relief="flat", width=20).grid(row=0, column=1, padx=6)
        tk.Button(btn_frame, text="Refresh", command=self.load_data,
                  bg="#e0e0e0", relief="flat", width=10).grid(row=0, column=2, padx=6)

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self.alert_rows = self.alert_dao.get_with_robot_names()
        for row in self.alert_rows:
            resolved_text = "Yes" if row["resolved"] else "No"
            self.tree.insert("", "end", iid=str(row["alert_id"]), values=(
                row["robot_name"], row["alert_type"].replace("_", " ").title(),
                row["severity"].title(), row["message"], str(row["created_at"]), resolved_text,
            ), tags=(row["severity"],))

    def resolve_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select an alert to resolve.")
            return
        alert_id = int(selected[0])
        self.alert_dao.resolve(alert_id)
        self.load_data()
        if self.on_change:
            self.on_change()

    def simulate_event(self):
        robots = self.robot_service.list_robots()
        if not robots:
            messagebox.showinfo("No robots", "No robots available to simulate an event for.")
            return
        import random
        robot = random.choice(robots)
        self.simulation_service.simulate_random_event(robot.robot_id)
        self.load_data()
        if self.on_change:
            self.on_change()
