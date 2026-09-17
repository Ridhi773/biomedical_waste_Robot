"""Robot Status screen — lists all robots with battery, status, and current location."""

import tkinter as tk
from tkinter import ttk

from services.robot_service import RobotService


class RobotStatusWindow(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Robot Status")
        self.geometry("520x360")
        self.robot_service = RobotService()

        tk.Label(self, text="Robot Status", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("name", "status", "battery", "location", "updated")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        headings = {
            "name": "Robot", "status": "Status", "battery": "Battery %",
            "location": "Location", "updated": "Last Updated",
        }
        widths = {"name": 90, "status": 90, "battery": 80, "location": 140, "updated": 130}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.tag_configure("low_battery", background="#fde3e3")
        self.tree.tag_configure("error", background="#ffd6d6")

        tk.Button(self, text="Refresh", command=self.load_data, bg="#2f7a63", fg="white",
                  relief="flat").pack(pady=(0, 10))

        self.load_data()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for robot in self.robot_service.list_robots():
            location_name = self.robot_service.get_robot_location_name(robot)
            tags = []
            if self.robot_service.is_battery_low(robot):
                tags.append("low_battery")
            if robot.status == "error":
                tags.append("error")
            self.tree.insert("", "end", values=(
                robot.name, robot.status.title(), f"{robot.battery_level:.1f}",
                location_name, robot.last_updated or "-",
            ), tags=tags)
