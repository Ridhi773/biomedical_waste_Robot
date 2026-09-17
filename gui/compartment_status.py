"""Compartment Status screen — shows every compartment per robot as a fill-level bar."""

import tkinter as tk
from tkinter import ttk

from services.robot_service import RobotService
from services.compartment_service import CompartmentService
from services.waste_service import WasteService


STATUS_COLORS = {"empty": "#8fbf8f", "partial": "#e6b84f", "full": "#d9534f"}


class CompartmentStatusWindow(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Compartment Status")
        self.geometry("520x460")

        self.robot_service = RobotService()
        self.compartment_service = CompartmentService()
        self.waste_service = WasteService()

        tk.Label(self, text="Compartment Status", font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10)

        tk.Button(self, text="Refresh", command=self.load_data, bg="#2f7a63", fg="white",
                  relief="flat").pack(pady=10)

        self.load_data()

    def load_data(self):
        for child in self.container.winfo_children():
            child.destroy()

        robots = self.robot_service.list_robots()
        for robot in robots:
            robot_frame = tk.LabelFrame(self.container, text=robot.name, font=("Segoe UI", 10, "bold"))
            robot_frame.pack(fill="x", pady=6)

            compartments = self.compartment_service.list_for_robot(robot.robot_id)
            if not compartments:
                tk.Label(robot_frame, text="No compartments configured.", fg="#888").pack(anchor="w", padx=8, pady=4)
                continue

            for comp in compartments:
                waste_type = self.waste_service.get_waste_type(comp.waste_type_id)
                waste_name = waste_type.name if waste_type else "Unknown waste"

                row = tk.Frame(robot_frame)
                row.pack(fill="x", padx=8, pady=4)

                tk.Label(row, text=f"{waste_name}", width=20, anchor="w").pack(side="left")

                bar_bg = tk.Frame(row, bg="#e0e0e0", width=180, height=16)
                bar_bg.pack(side="left", padx=6)
                bar_bg.pack_propagate(False)

                fill_width = int(180 * min(comp.fill_percent, 100) / 100)
                color = STATUS_COLORS.get(comp.status, "#8fbf8f")
                bar_fg = tk.Frame(bar_bg, bg=color, width=fill_width, height=16)
                bar_fg.place(x=0, y=0)

                tk.Label(row, text=f"{comp.fill_percent}% ({comp.current_fill_kg}/{comp.capacity_kg} kg)",
                         width=22).pack(side="left")
