"""
Disposal Verification screen - the second QR checkpoint, at the disposal
site. Verifies the destination, then lets you confirm final disposal,
which empties the compartment and closes out the transport.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from services.transport_service import TransportService
from services.qr_service import QRService
from services.disposal_service import DisposalService
from dao.destination_dao import DestinationDAO


class DisposalVerificationWindow(tk.Toplevel):

    def __init__(self, master, on_change=None):
        super().__init__(master)
        self.title("Disposal Verification - Destination QR")
        self.geometry("480x420")
        self.on_change = on_change

        self.transport_service = TransportService()
        self.qr_service = QRService()
        self.disposal_service = DisposalService()
        self.destination_dao = DestinationDAO()

        tk.Label(self, text="Destination QR & Disposal Confirmation",
                 font=("Segoe UI", 13, "bold")).pack(pady=10)
        tk.Label(
            self, fg="#666", wraplength=420, justify="left",
            text="Once pickup is verified, scan the destination's QR here. A match "
                 "lets you confirm final disposal, which resets the compartment.",
        ).pack(padx=20, pady=(0, 10))

        form = tk.Frame(self)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Transport (pickup verified):").grid(row=0, column=0, sticky="w", pady=6)
        self.transport_var = tk.StringVar()
        self.transport_combo = ttk.Combobox(form, textvariable=self.transport_var, state="readonly", width=34)
        self.transport_combo.grid(row=0, column=1, pady=6)

        tk.Label(form, text="Destination:").grid(row=1, column=0, sticky="w", pady=6)
        self.destination_var = tk.StringVar()
        self.destination_combo = ttk.Combobox(form, textvariable=self.destination_var, state="readonly", width=34)
        self.destination_combo.grid(row=1, column=1, pady=6)
        self.destination_combo.bind("<<ComboboxSelected>>", self._on_destination_selected)

        self.expected_label = tk.Label(form, text="", fg="#555")
        self.expected_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 6))

        tk.Label(form, text="Scanned code:").grid(row=3, column=0, sticky="w", pady=6)
        self.scanned_var = tk.StringVar()
        tk.Entry(form, textvariable=self.scanned_var, width=36).grid(row=3, column=1, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Fill Correct Code (demo)", command=self._fill_correct,
                  bg="#e0e0e0", relief="flat").grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Scan at Destination", command=self._scan,
                  bg="#3a6ea5", fg="white", relief="flat", width=18).grid(row=0, column=1, padx=4)

        self.result_label = tk.Label(self, text="", font=("Segoe UI", 10, "bold"))
        self.result_label.pack(pady=6)

        tk.Button(self, text="Confirm Disposal", command=self._confirm_disposal,
                  bg="#2f7a63", fg="white", relief="flat", width=20).pack(pady=6)

        tk.Button(self, text="Refresh", command=self.load_data, bg="#e0e0e0", relief="flat").pack(pady=(6, 0))

        self.load_data()

    def load_data(self):
        self.transports = self.transport_service.list_by_status("pickup_verified")
        self.transport_combo["values"] = [
            f"#{t.transport_id} - Robot {t.robot_id}, Compartment #{t.compartment_id}"
            for t in self.transports
        ]
        if self.transports:
            self.transport_combo.current(0)

        self.destinations = self.destination_dao.get_all()
        self.destination_combo["values"] = [d.name for d in self.destinations]
        if self.destinations:
            self.destination_combo.current(0)
            self._on_destination_selected()

    def _on_destination_selected(self, event=None):
        idx = self.destination_combo.current()
        if idx < 0:
            return
        destination = self.destinations[idx]
        # NOTE: shown for demo transparency only - a real scan wouldn't reveal this.
        self.expected_label.config(text=f"(Demo hint) Destination QR code: {destination.qr_code}")

    def _fill_correct(self):
        idx = self.destination_combo.current()
        if idx < 0:
            return
        self.scanned_var.set(self.destinations[idx].qr_code)

    def _selected_transport(self):
        idx = self.transport_combo.current()
        return self.transports[idx] if idx >= 0 else None

    def _selected_destination(self):
        idx = self.destination_combo.current()
        return self.destinations[idx] if idx >= 0 else None

    def _scan(self):
        transport = self._selected_transport()
        destination = self._selected_destination()
        if transport is None or destination is None:
            messagebox.showwarning("Missing selection", "Select a transport and a destination.")
            return
        ok, msg = self.qr_service.verify_destination(
            transport.transport_id, destination.destination_id, self.scanned_var.get()
        )
        self.result_label.config(text=msg, fg="#2f7a63" if ok else "#d9534f")
        self.scanned_var.set("")
        if self.on_change:
            self.on_change()

    def _confirm_disposal(self):
        transport = self._selected_transport()
        if transport is None:
            messagebox.showwarning("No selection", "Select a transport first.")
            return
        ok, msg = self.disposal_service.confirm_disposal(transport.transport_id)
        self.result_label.config(text=msg, fg="#2f7a63" if ok else "#d9534f")
        self.load_data()
        if self.on_change:
            self.on_change()
