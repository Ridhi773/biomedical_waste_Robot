"""
Main application window. Shows an at-a-glance summary and buttons to open
each of the other screens in its own Toplevel window. Only reachable after
a successful admin login (see gui/login.py + main.py).
"""

import tkinter as tk
from tkinter import ttk

from services.robot_service import RobotService
from services.compartment_service import CompartmentService
from services.transport_service import TransportService
from dao.alert_dao import AlertDAO
from dao.collection_dao import CollectionDAO
from dao.complaint_dao import ComplaintDAO

from gui.robot_status import RobotStatusWindow
from gui.waste_detection import WasteDetectionWindow
from gui.manual_collection import ManualCollectionWindow
from gui.compartment_status import CompartmentStatusWindow
from gui.collection_history import CollectionHistoryWindow
from gui.alerts import AlertsWindow
from gui.robot_tracking import RobotTrackingWindow
from gui.transport_requests import TransportRequestsWindow
from gui.driver_scanner import DriverScannerWindow
from gui.disposal_verification import DisposalVerificationWindow
from gui.qr_verification import QRVerificationLogWindow
from gui.complaints import ComplaintsWindow


class Dashboard(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Biomedical Waste Robot - Control Dashboard")
        self.geometry("1100x720")
        self.configure(bg="#f4f6f8")
        self.resizable(True, True)
        try:
            self.state("zoomed")   # opens maximized on Windows
        except tk.TclError:
            pass   # falls back to the geometry() size above on other platforms

        self.robot_service = RobotService()
        self.compartment_service = CompartmentService()
        self.transport_service = TransportService()
        self.alert_dao = AlertDAO()
        self.collection_dao = CollectionDAO()
        self.complaint_dao = ComplaintDAO()

        self._build_header()
        self._build_summary()
        self._build_nav_buttons()
        self.refresh_summary()

    # ---------- layout ----------

    def _build_header(self):
        header = tk.Frame(self, bg="#1b3a4b", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Biomedical Waste Robot - Control Dashboard",
            fg="white", bg="#1b3a4b", font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=20, pady=15)

    def _build_summary(self):
        self.summary_frame = tk.Frame(self, bg="#f4f6f8")
        self.summary_frame.pack(fill="x", padx=20, pady=15)

        self.card_robots = self._make_card(self.summary_frame, "Robots", "0", 0)
        self.card_alerts = self._make_card(self.summary_frame, "Open Alerts", "0", 1)
        self.card_full = self._make_card(self.summary_frame, "Full Compartments", "0", 2)
        self.card_collections = self._make_card(self.summary_frame, "Total Collections", "0", 3)
        self.card_pending_transport = self._make_card(self.summary_frame, "Pending Transports", "0", 4)
        self.card_complaints = self._make_card(self.summary_frame, "Open Complaints", "0", 5)

        for i in range(6):
            self.summary_frame.grid_columnconfigure(i, weight=1)

    def _make_card(self, parent, title, value, col):
        frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
        frame.grid(row=0, column=col, padx=8, sticky="nsew")
        value_lbl = tk.Label(frame, text=value, font=("Segoe UI", 20, "bold"), bg="white", fg="#1b3a4b")
        value_lbl.pack(pady=(14, 0))
        tk.Label(frame, text=title, font=("Segoe UI", 9), bg="white", fg="#555").pack(pady=(0, 14))
        return value_lbl

    def _build_nav_buttons(self):
        nav = tk.Frame(self, bg="#f4f6f8")
        nav.pack(fill="both", expand=True, padx=20, pady=10)

        buttons = [
            ("Robot Status", self.open_robot_status),
            ("Waste Detection", self.open_waste_detection),
            ("Manual Collection", self.open_manual_collection),
            ("Compartment Status", self.open_compartment_status),
            ("Robot Tracking", self.open_robot_tracking),
            ("Collection History", self.open_collection_history),
            ("Transport Requests", self.open_transport_requests),
            ("Driver Scanner (Pickup QR)", self.open_driver_scanner),
            ("Disposal Verification", self.open_disposal_verification),
            ("QR Verification Log", self.open_qr_verification_log),
            ("Alerts", self.open_alerts),
            ("Complaints", self.open_complaints),
        ]

        cols = 3
        for i, (label, cmd) in enumerate(buttons):
            btn = tk.Button(
                nav, text=label, command=cmd, font=("Segoe UI", 11),
                bg="#2f7a63", fg="white", activebackground="#25604e",
                relief="flat", height=3, cursor="hand2",
            )
            btn.grid(row=i // cols, column=i % cols, sticky="nsew", padx=8, pady=8)

        for c in range(cols):
            nav.grid_columnconfigure(c, weight=1)
        for r in range((len(buttons) + cols - 1) // cols):
            nav.grid_rowconfigure(r, weight=1)

        refresh_btn = tk.Button(
            self, text="Refresh Summary", command=self.refresh_summary,
            font=("Segoe UI", 9), bg="#e0e0e0", relief="flat", cursor="hand2",
        )
        refresh_btn.pack(pady=(0, 12))

    # ---------- data ----------

    def refresh_summary(self):
        robots = self.robot_service.list_robots()
        compartments = self.compartment_service.list_all()
        open_alerts = self.alert_dao.get_unresolved()
        collections = self.collection_dao.get_all()
        pending_transports = self.transport_service.list_by_status("pending")
        open_complaints = self.complaint_dao.get_open()

        self.card_robots.config(text=str(len(robots)))
        self.card_alerts.config(text=str(len(open_alerts)))
        self.card_full.config(text=str(sum(1 for c in compartments if c.status == "full")))
        self.card_collections.config(text=str(len(collections)))
        self.card_pending_transport.config(text=str(len(pending_transports)))
        self.card_complaints.config(text=str(len(open_complaints)))

    # ---------- navigation ----------

    def open_robot_status(self):
        RobotStatusWindow(self)

    def open_waste_detection(self):
        WasteDetectionWindow(self, on_change=self.refresh_summary)

    def open_manual_collection(self):
        ManualCollectionWindow(self, on_change=self.refresh_summary)

    def open_compartment_status(self):
        CompartmentStatusWindow(self)

    def open_collection_history(self):
        CollectionHistoryWindow(self)

    def open_alerts(self):
        AlertsWindow(self, on_change=self.refresh_summary)

    def open_robot_tracking(self):
        RobotTrackingWindow(self, on_change=self.refresh_summary)

    def open_transport_requests(self):
        TransportRequestsWindow(self, on_change=self.refresh_summary)

    def open_driver_scanner(self):
        DriverScannerWindow(self, on_change=self.refresh_summary)

    def open_disposal_verification(self):
        DisposalVerificationWindow(self, on_change=self.refresh_summary)

    def open_qr_verification_log(self):
        QRVerificationLogWindow(self)

    def open_complaints(self):
        ComplaintsWindow(self, on_change=self.refresh_summary)


if __name__ == "__main__":
    # Allows running the dashboard directly during development, bypassing login.
    app = Dashboard()
    app.mainloop()
