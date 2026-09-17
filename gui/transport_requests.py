"""
Transport Requests screen - request a transport for a full compartment,
assign a driver, and start the transport (ready for the pickup QR scan
in Driver Scanner).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from services.robot_service import RobotService
from services.compartment_service import CompartmentService
from services.transport_service import TransportService

STATUS_COLORS = {
    "pending": "#fff6db", "assigned": "#e3edfa", "in_progress": "#e3edfa",
    "pickup_verified": "#eaf5e9", "completed": "#eaf5e9", "cancelled": "#f0f0f0",
}


class TransportRequestsWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Transport Requests")
        self.geometry("760x520")
        self.on_change = on_change

        self.robot_service = RobotService()
        self.compartment_service = CompartmentService()
        self.transport_service = TransportService()

        tk.Label(self, text="Transport Requests", font=("Segoe UI", 14, "bold")).pack(pady=10)

        request_frame = tk.LabelFrame(self, text="Request transport for a full compartment")
        request_frame.pack(fill="x", padx=15, pady=8)

        tk.Label(request_frame, text="Full compartment:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.full_compartment_var = tk.StringVar()
        self.full_compartment_combo = ttk.Combobox(
            request_frame, textvariable=self.full_compartment_var, state="readonly", width=40
        )
        self.full_compartment_combo.grid(row=0, column=1, padx=8, pady=8)
        tk.Button(request_frame, text="Request Transport", command=self._request_transport,
                  bg="#2f7a63", fg="white", relief="flat").grid(row=0, column=2, padx=8)

        columns = ("id", "robot", "compartment", "driver", "destination", "status", "requested")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        headings = {
            "id": "ID", "robot": "Robot", "compartment": "Bin", "driver": "Driver",
            "destination": "Destination", "status": "Status", "requested": "Requested At",
        }
        widths = {"id": 30, "robot": 70, "compartment": 90, "driver": 110,
                  "destination": 140, "status": 100, "requested": 130}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(fill="both", expand=True, padx=15, pady=8)

        for status, color in STATUS_COLORS.items():
            self.tree.tag_configure(status, background=color)

        action_frame = tk.LabelFrame(self, text="Actions for selected request")
        action_frame.pack(fill="x", padx=15, pady=8)

        tk.Label(action_frame, text="Driver:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.driver_var = tk.StringVar()
        self.driver_combo = ttk.Combobox(action_frame, textvariable=self.driver_var, state="readonly", width=24)
        self.driver_combo.grid(row=0, column=1, padx=8, pady=8)
        tk.Button(action_frame, text="Assign Driver", command=self._assign_driver,
                  bg="#3a6ea5", fg="white", relief="flat").grid(row=0, column=2, padx=8)

        tk.Button(action_frame, text="Start Transport", command=self._start_transport,
                  bg="#3a6ea5", fg="white", relief="flat").grid(row=0, column=3, padx=8)

        tk.Button(self, text="Refresh", command=self.load_data,
                  bg="#e0e0e0", relief="flat").pack(pady=(0, 10))

        self.status_label = tk.Label(self, text="", fg="#333")
        self.status_label.pack()

        self.load_data()

    def load_data(self):
        # full compartments available to request transport for
        full_compartments = [
            c for c in self.compartment_service.list_all() if c.status == "full"
        ]
        self.full_compartments = full_compartments
        self.full_compartment_combo["values"] = [
            f"Robot #{c.robot_id} - Compartment #{c.compartment_id} ({c.qr_code})"
            for c in full_compartments
        ]

        self.drivers = self.transport_service.list_available_drivers()
        self.driver_combo["values"] = [f"{d.name} ({d.phone})" for d in self.drivers]

        self.tree.delete(*self.tree.get_children())
        self.transport_rows = self.transport_service.list_with_details()
        for row in self.transport_rows:
            self.tree.insert("", "end", iid=str(row["transport_id"]), values=(
                row["transport_id"], row["robot_name"], f"#{row['compartment_id']} ({row['compartment_qr']})",
                row["driver_name"] or "-", row["destination_name"] or "-",
                row["status"].replace("_", " ").title(), str(row["requested_at"]),
            ), tags=(row["status"],))

    def _request_transport(self):
        idx = self.full_compartment_combo.current()
        if idx < 0:
            messagebox.showwarning("No selection", "Select a full compartment first.")
            return
        compartment = self.full_compartments[idx]
        ok, msg = self.transport_service.create_request(compartment.robot_id, compartment.compartment_id)
        self.status_label.config(text=msg, fg="#2f7a63" if ok else "#d9534f")
        self.load_data()
        if self.on_change:
            self.on_change()

    def _selected_transport_id(self):
        selected = self.tree.selection()
        return int(selected[0]) if selected else None

    def _assign_driver(self):
        transport_id = self._selected_transport_id()
        d_idx = self.driver_combo.current()
        if transport_id is None:
            messagebox.showwarning("No selection", "Select a transport request first.")
            return
        if d_idx < 0:
            messagebox.showwarning("No driver", "Select a driver to assign.")
            return
        driver = self.drivers[d_idx]
        ok, msg = self.transport_service.assign_driver(transport_id, driver.driver_id)
        self.status_label.config(text=msg, fg="#2f7a63" if ok else "#d9534f")
        self.load_data()
        if self.on_change:
            self.on_change()

    def _start_transport(self):
        transport_id = self._selected_transport_id()
        if transport_id is None:
            messagebox.showwarning("No selection", "Select a transport request first.")
            return
        ok, msg = self.transport_service.start_transport(transport_id)
        self.status_label.config(text=msg, fg="#2f7a63" if ok else "#d9534f")
        self.load_data()
        if self.on_change:
            self.on_change()
