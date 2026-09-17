"""
Manual Collection screen - dedicated fallback used when a robot has a
technical issue and staff need to log its waste collections by hand,
including switching the robot in and out of 'manual' status.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from services.robot_service import RobotService
from services.compartment_service import CompartmentService
from services.collection_service import CollectionService
from services.waste_service import WasteService
from utils.validators import is_positive_number


class ManualCollectionWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Manual Collection (Technical Issue Mode)")
        self.geometry("440x420")
        self.on_change = on_change

        self.robot_service = RobotService()
        self.compartment_service = CompartmentService()
        self.collection_service = CollectionService()
        self.waste_service = WasteService()

        tk.Label(self, text="Manual Collection Mode", font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(
            self, fg="#666", wraplength=380, justify="left",
            text="Use this when a robot can't operate automatically. Switch it to "
                 "'manual' status, then log its waste collections by hand until the "
                 "issue is resolved.",
        ).pack(padx=20, pady=(0, 10))

        form = tk.Frame(self)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Robot:").grid(row=0, column=0, sticky="w", pady=6)
        self.robot_var = tk.StringVar()
        self.robot_combo = ttk.Combobox(form, textvariable=self.robot_var, state="readonly", width=26)
        self.robot_combo.grid(row=0, column=1, pady=6)
        self.robot_combo.bind("<<ComboboxSelected>>", self._on_robot_selected)

        self.robot_status_label = tk.Label(form, text="", fg="#333")
        self.robot_status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))

        mode_frame = tk.Frame(self)
        mode_frame.pack(pady=4)
        tk.Button(mode_frame, text="Set to Manual (issue)", command=lambda: self._set_status("manual"),
                  bg="#c0562e", fg="white", relief="flat", width=20).grid(row=0, column=0, padx=4)
        tk.Button(mode_frame, text="Set back to Idle (resolved)", command=lambda: self._set_status("idle"),
                  bg="#2f7a63", fg="white", relief="flat", width=22).grid(row=0, column=1, padx=4)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=14)

        form2 = tk.Frame(self)
        form2.pack(fill="x", padx=20)

        tk.Label(form2, text="Compartment:").grid(row=0, column=0, sticky="w", pady=6)
        self.compartment_var = tk.StringVar()
        self.compartment_combo = ttk.Combobox(form2, textvariable=self.compartment_var, state="readonly", width=26)
        self.compartment_combo.grid(row=0, column=1, pady=6)

        tk.Label(form2, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=6)
        self.weight_var = tk.StringVar()
        tk.Entry(form2, textvariable=self.weight_var, width=28).grid(row=1, column=1, pady=6)

        tk.Label(form2, text="Location:").grid(row=2, column=0, sticky="w", pady=6)
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(form2, textvariable=self.location_var, state="readonly", width=26)
        self.location_combo.grid(row=2, column=1, pady=6)

        tk.Button(self, text="Log Manual Collection", command=self._log_collection,
                  bg="#3a6ea5", fg="white", relief="flat", width=22).pack(pady=14)

        self.status_label = tk.Label(self, text="", fg="#333")
        self.status_label.pack()

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
        self.robot_status_label.config(text=f"Current status: {robot.status.title()}")
        self.compartments = self.compartment_service.list_for_robot(robot.robot_id)
        self.compartment_combo["values"] = [
            f"#{c.compartment_id} ({c.fill_percent}% full)" for c in self.compartments
        ]
        if self.compartments:
            self.compartment_combo.current(0)

    def _set_status(self, status):
        idx = self.robot_combo.current()
        if idx < 0:
            messagebox.showwarning("No robot", "Select a robot first.")
            return
        robot = self.robots[idx]
        self.robot_service.set_status(robot.robot_id, status)
        self._load_lookups()
        if self.on_change:
            self.on_change()

    def _log_collection(self):
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
