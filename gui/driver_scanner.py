"""
Driver Scanner screen - simulates the driver scanning a compartment's QR
code before dumping it. There's no real scanner hardware, so the "scan" is
a code you pick or type; a wrong code demonstrates the mismatch/alert path.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from services.transport_service import TransportService
from services.qr_service import QRService


class DriverScannerWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Driver Scanner - Pickup QR")
        self.geometry("460x360")
        self.on_change = on_change

        self.transport_service = TransportService()
        self.qr_service = QRService()

        tk.Label(self, text="Pickup QR Scan", font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(
            self, fg="#666", wraplength=400, justify="left",
            text="Select an in-progress transport, then simulate scanning the bin's "
                 "QR code. A correct code authorizes dumping; a wrong one is denied "
                 "and raises an alert.",
        ).pack(padx=20, pady=(0, 10))

        form = tk.Frame(self)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Transport (in progress):").grid(row=0, column=0, sticky="w", pady=6)
        self.transport_var = tk.StringVar()
        self.transport_combo = ttk.Combobox(form, textvariable=self.transport_var, state="readonly", width=32)
        self.transport_combo.grid(row=0, column=1, pady=6)
        self.transport_combo.bind("<<ComboboxSelected>>", self._on_transport_selected)

        self.expected_label = tk.Label(form, text="", fg="#555")
        self.expected_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))

        tk.Label(form, text="Scanned code:").grid(row=2, column=0, sticky="w", pady=6)
        self.scanned_var = tk.StringVar()
        tk.Entry(form, textvariable=self.scanned_var, width=34).grid(row=2, column=1, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Fill Correct Code (demo)", command=self._fill_correct,
                  bg="#e0e0e0", relief="flat").grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Scan QR", command=self._scan,
                  bg="#2f7a63", fg="white", relief="flat", width=14).grid(row=0, column=1, padx=4)

        self.result_label = tk.Label(self, text="", font=("Segoe UI", 10, "bold"))
        self.result_label.pack(pady=10)

        tk.Button(self, text="Refresh", command=self.load_data, bg="#e0e0e0", relief="flat").pack()

        self.load_data()

    def load_data(self):
        self.transports = self.transport_service.list_by_status("in_progress")
        self.transport_combo["values"] = [
            f"#{t.transport_id} - Robot {t.robot_id}, Compartment #{t.compartment_id}"
            for t in self.transports
        ]
        if self.transports:
            self.transport_combo.current(0)
            self._on_transport_selected()
        else:
            self.expected_label.config(text="No transports are currently in progress.")

    def _on_transport_selected(self, event=None):
        idx = self.transport_combo.current()
        if idx < 0:
            return
        # NOTE: showing the expected code here is for demo transparency only -
        # a real scanner wouldn't reveal this to the driver ahead of time.
        from dao.compartment_dao import CompartmentDAO
        transport = self.transports[idx]
        compartment = CompartmentDAO().get_by_id(transport.compartment_id)
        self.expected_label.config(text=f"(Demo hint) Bin QR code: {compartment.qr_code}")

    def _fill_correct(self):
        idx = self.transport_combo.current()
        if idx < 0:
            return
        from dao.compartment_dao import CompartmentDAO
        transport = self.transports[idx]
        compartment = CompartmentDAO().get_by_id(transport.compartment_id)
        self.scanned_var.set(compartment.qr_code)

    def _scan(self):
        idx = self.transport_combo.current()
        if idx < 0:
            messagebox.showwarning("No selection", "Select a transport first.")
            return
        transport = self.transports[idx]
        ok, msg = self.qr_service.verify_pickup(transport.transport_id, self.scanned_var.get())
        self.result_label.config(text=msg, fg="#2f7a63" if ok else "#d9534f")
        self.scanned_var.set("")
        self.load_data()
        if self.on_change:
            self.on_change()
