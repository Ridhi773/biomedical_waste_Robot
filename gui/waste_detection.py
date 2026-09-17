"""
Waste Detection screen — logs a waste pickup into a robot's compartment,
either manually or via a 'Simulate Detection' button (since there's no real sensor feed).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from services.robot_service import RobotService
from services.compartment_service import CompartmentService
from services.collection_service import CollectionService
from services.simulation_service import SimulationService
from services.waste_service import WasteService
from utils.validators import is_positive_number


class WasteDetectionWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Waste Detection")
        self.geometry("420x360")
        self.on_change = on_change

        self.robot_service = RobotService()
        self.compartment_service = CompartmentService()
        self.collection_service = CollectionService()
        self.simulation_service = SimulationService()
        self.waste_service = WasteService()

        tk.Label(self, text="Log a Waste Collection", font=("Segoe UI", 14, "bold")).pack(pady=10)

        form = tk.Frame(self)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Robot:").grid(row=0, column=0, sticky="w", pady=6)
        self.robot_var = tk.StringVar()
        self.robot_combo = ttk.Combobox(form, textvariable=self.robot_var, state="readonly", width=28)
        self.robot_combo.grid(row=0, column=1, pady=6)
        self.robot_combo.bind("<<ComboboxSelected>>", self._on_robot_selected)

        tk.Label(form, text="Compartment:").grid(row=1, column=0, sticky="w", pady=6)
        self.compartment_var = tk.StringVar()
        self.compartment_combo = ttk.Combobox(form, textvariable=self.compartment_var, state="readonly", width=28)
        self.compartment_combo.grid(row=1, column=1, pady=6)

        tk.Label(form, text="Weight (kg):").grid(row=2, column=0, sticky="w", pady=6)
        self.weight_var = tk.StringVar()
        tk.Entry(form, textvariable=self.weight_var, width=30).grid(row=2, column=1, pady=6)

        tk.Label(form, text="Location:").grid(row=3, column=0, sticky="w", pady=6)
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(form, textvariable=self.location_var, state="readonly", width=28)
        self.location_combo.grid(row=3, column=1, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=16)
        tk.Button(btn_frame, text="Record Collection", command=self.record,
                  bg="#2f7a63", fg="white", relief="flat", width=18).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Simulate Detection", command=self.simulate,
                  bg="#3a6ea5", fg="white", relief="flat", width=18).grid(row=0, column=1, padx=6)

        self.status_label = tk.Label(self, text="", fg="#333")
        self.status_label.pack(pady=6)

        self._load_lookups()

    def _load_lookups(self):
        self.robots = self.robot_service.list_robots()
        self.locations = self.waste_service.list_locations()

        self.robot_combo["values"] = [r.name for r in self.robots]
        self.location_combo["values"] = [l.name for l in self.locations]

        if self.robots:
            self.robot_combo.current(0)
            self._on_robot_selected()
        if self.locations:
            self.location_combo.current(0)

    def _on_robot_selected(self, event=None):
        idx = self.robot_combo.current()
        if idx < 0:
            return
        robot = self.robots[idx]
        self.compartments = self.compartment_service.list_for_robot(robot.robot_id)
        self.compartment_combo["values"] = [
            f"#{c.compartment_id} ({c.fill_percent}% full)" for c in self.compartments
        ]
        if self.compartments:
            self.compartment_combo.current(0)

    def record(self):
        r_idx, c_idx, l_idx = self.robot_combo.current(), self.compartment_combo.current(), self.location_combo.current()
        if r_idx < 0 or c_idx < 0:
            messagebox.showwarning("Missing info", "Select a robot and compartment.")
            return
        if not is_positive_number(self.weight_var.get()):
            messagebox.showwarning("Invalid weight", "Enter a positive weight in kg.")
            return

        robot = self.robots[r_idx]
        compartment = self.compartments[c_idx]
        location = self.locations[l_idx] if l_idx >= 0 else None

        ok, msg = self.collection_service.record_collection(
            robot_id=robot.robot_id,
            compartment_id=compartment.compartment_id,
            waste_type_id=compartment.waste_type_id,
            weight_kg=self.weight_var.get(),
            location_id=location.location_id if location else None,
        )
        self.status_label.config(text=msg, fg="#2f7a63" if ok else "#d9534f")
        if ok:
            self.weight_var.set("")
            self._on_robot_selected()
            if self.on_change:
                self.on_change()

    def simulate(self):
        r_idx = self.robot_combo.current()
        if r_idx < 0:
            messagebox.showwarning("Missing info", "Select a robot first.")
            return
        robot = self.robots[r_idx]
        ok, msg = self.simulation_service.simulate_waste_detection(robot.robot_id)
        self.status_label.config(text=f"[Simulated] {msg}", fg="#2f7a63" if ok else "#d9534f")
        if ok:
            self._on_robot_selected()
            if self.on_change:
                self.on_change()
