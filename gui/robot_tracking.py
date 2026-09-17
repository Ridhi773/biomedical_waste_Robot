"""
Robot Tracking screen — draws all facility locations as nodes on a canvas,
highlights each robot's current location, and lets you simulate movement.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math

from services.robot_service import RobotService
from services.tracking_service import TrackingService
from services.simulation_service import SimulationService

ROBOT_COLORS = ["#3a6ea5", "#c0562e", "#7a3ac0", "#2f7a63", "#a52e6e"]


class RobotTrackingWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Robot Tracking")
        self.geometry("560x520")
        self.on_change = on_change

        self.robot_service = RobotService()
        self.tracking_service = TrackingService()
        self.simulation_service = SimulationService()

        tk.Label(self, text="Robot Tracking", font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.canvas = tk.Canvas(self, width=520, height=340, bg="white", highlightthickness=1,
                                 highlightbackground="#ccc")
        self.canvas.pack(padx=10, pady=10)

        control = tk.Frame(self)
        control.pack(fill="x", padx=20)

        tk.Label(control, text="Robot:").grid(row=0, column=0, sticky="w")
        self.robot_var = tk.StringVar()
        self.robot_combo = ttk.Combobox(control, textvariable=self.robot_var, state="readonly", width=25)
        self.robot_combo.grid(row=0, column=1, padx=6)

        tk.Button(control, text="Simulate Move", command=self.simulate_move,
                  bg="#3a6ea5", fg="white", relief="flat").grid(row=0, column=2, padx=6)
        tk.Button(control, text="Refresh", command=self.load_data,
                  bg="#e0e0e0", relief="flat").grid(row=0, column=3, padx=6)

        self.legend = tk.Label(self, text="", justify="left", anchor="w", font=("Segoe UI", 9))
        self.legend.pack(fill="x", padx=20, pady=(10, 0))

        self.load_data()

    def load_data(self):
        self.robots = self.robot_service.list_robots()
        self.locations = self.tracking_service.get_all_locations()
        self.robot_combo["values"] = [r.name for r in self.robots]
        if self.robots:
            self.robot_combo.current(0)
        self._draw()

    def _location_positions(self):
        """Arrange locations evenly around a circle for a simple facility map."""
        positions = {}
        n = len(self.locations)
        if n == 0:
            return positions
        cx, cy, radius = 260, 170, 130
        for i, loc in enumerate(self.locations):
            angle = (2 * math.pi * i) / n
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions[loc.location_id] = (x, y)
        return positions

    def _draw(self):
        self.canvas.delete("all")
        positions = self._location_positions()

        for loc in self.locations:
            x, y = positions[loc.location_id]
            self.canvas.create_oval(x - 26, y - 26, x + 26, y + 26, fill="#eef2f5", outline="#999")
            self.canvas.create_text(x, y, text=loc.name, width=70, font=("Segoe UI", 7), justify="center")

        legend_lines = []
        for i, robot in enumerate(self.robots):
            color = ROBOT_COLORS[i % len(ROBOT_COLORS)]
            if robot.current_location_id in positions:
                x, y = positions[robot.current_location_id]
                offset = (i - len(self.robots) / 2) * 8
                self.canvas.create_oval(
                    x - 8 + offset, y - 8 - 30, x + 8 + offset, y + 8 - 30,
                    fill=color, outline=""
                )
            legend_lines.append(f"● {robot.name} — {robot.status.title()}, battery {robot.battery_level:.0f}%")

        self.legend.config(text="\n".join(legend_lines))

    def simulate_move(self):
        idx = self.robot_combo.current()
        if idx < 0:
            messagebox.showinfo("No robot", "Select a robot first.")
            return
        robot = self.robots[idx]
        ok, msg = self.simulation_service.simulate_movement(robot.robot_id)
        if not ok:
            messagebox.showwarning("Move failed", msg)
        self.load_data()
        if self.on_change:
            self.on_change()
