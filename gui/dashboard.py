"""
Main application window. Shows an at-a-glance summary and tabbed navigation
to each of the other screens, opened in its own Toplevel window. Only
reachable after a successful admin login (see gui/login.py + main.py).

Color palette is pulled from the project logo (navy -> teal -> green).
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

# ---- palette (matches the InitCode logo: navy -> teal -> green) ----
NAVY = "#0f2d46"
TEAL = "#1a7f8c"
TEAL_DARK = "#145f69"
GREEN = "#3fae5c"
BG = "#f4f6f8"
RED_ACCENT = "#d9534f"
AMBER_ACCENT = "#e0a53c"


class Dashboard(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Biomedical Waste Robot - Control Dashboard")
        self.geometry("1100x720")
        self.configure(bg=BG)
        self.resizable(True, True)
        try:
            self.state("zoomed")   # opens maximized on Windows
        except tk.TclError:
            pass   # falls back to the geometry() size above on other platforms

        try:
            self.logo_img = tk.PhotoImage(file="assets/images/logo.png")
        except tk.TclError:
            self.logo_img = None   # missing/unreadable file - app still runs without it

        self.robot_service = RobotService()
        self.compartment_service = CompartmentService()
        self.transport_service = TransportService()
        self.alert_dao = AlertDAO()
        self.collection_dao = CollectionDAO()
        self.complaint_dao = ComplaintDAO()

        self._build_header()
        self._build_summary()
        self._build_tabs()
        self.refresh_summary()

    # ---------- layout ----------

    def _build_header(self):
        header = tk.Frame(self, bg=NAVY, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Biomedical Waste Robot - Control Dashboard",
            fg="white", bg=NAVY, font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=20, pady=15)

        if self.logo_img is not None:
            tk.Label(header, image=self.logo_img, bg=NAVY).pack(side="right", padx=20)

    def _build_summary(self):
        self.summary_frame = tk.Frame(self, bg=BG)
        self.summary_frame.pack(fill="x", padx=20, pady=15)

        self.card_robots = self._make_card(self.summary_frame, "Robots", 0, TEAL)
        self.card_alerts = self._make_card(self.summary_frame, "Open Alerts", 1, RED_ACCENT)
        self.card_full = self._make_card(self.summary_frame, "Full Compartments", 2, AMBER_ACCENT)
        self.card_collections = self._make_card(self.summary_frame, "Total Collections", 3, TEAL)
        self.card_pending_transport = self._make_card(self.summary_frame, "Pending Transports", 4, AMBER_ACCENT)
        self.card_complaints = self._make_card(self.summary_frame, "Open Complaints", 5, RED_ACCENT)

        for i in range(6):
            self.summary_frame.grid_columnconfigure(i, weight=1)

    def _make_card(self, parent, title, col, accent_color):
        outer = tk.Frame(parent, bg=accent_color)
        outer.grid(row=0, column=col, padx=8, sticky="nsew")

        inner = tk.Frame(outer, bg="white")
        inner.pack(fill="both", expand=True, padx=(4, 0))

        value_lbl = tk.Label(inner, text="0", font=("Segoe UI", 20, "bold"), bg="white", fg=NAVY)
        value_lbl.pack(pady=(14, 0))
        tk.Label(inner, text=title, font=("Segoe UI", 9), bg="white", fg="#555").pack(pady=(0, 14))
        return value_lbl

    def _build_tabs(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab", padding=(18, 10), font=("Segoe UI", 10, "bold"),
            background="#dfe6e9", foreground=NAVY,
        )
        style.map("TNotebook.Tab", background=[("selected", TEAL)], foreground=[("selected", "white")])

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        operations_tab = tk.Frame(notebook, bg=BG)
        transport_tab = tk.Frame(notebook, bg=BG)
        admin_tab = tk.Frame(notebook, bg=BG)

        notebook.add(operations_tab, text="Operations")
        notebook.add(transport_tab, text="Transport & Disposal")
        notebook.add(admin_tab, text="Admin")

        self._add_nav_grid(operations_tab, [
            ("Robot Status", self.open_robot_status),
            ("Waste Detection", self.open_waste_detection),
            ("Manual Collection", self.open_manual_collection),
            ("Compartment Status", self.open_compartment_status),
            ("Robot Tracking", self.open_robot_tracking),
        ], TEAL, TEAL_DARK)

        self._add_nav_grid(transport_tab, [
            ("Transport Requests", self.open_transport_requests),
            ("Driver Scanner (Pickup QR)", self.open_driver_scanner),
            ("Disposal Verification", self.open_disposal_verification),
            ("QR Verification Log", self.open_qr_verification_log),
        ], GREEN, "#2d8a45")

        self._add_nav_grid(admin_tab, [
            ("Collection History", self.open_collection_history),
            ("Alerts", self.open_alerts),
            ("Complaints", self.open_complaints),
        ], NAVY, "#08192a")

        refresh_btn = tk.Button(
            self, text="Refresh Summary", command=self.refresh_summary,
            font=("Segoe UI", 9), bg="#e0e0e0", relief="flat", cursor="hand2",
        )
        refresh_btn.pack(pady=(0, 12))

    def _add_nav_grid(self, parent, buttons, bg_color, active_color, cols=2):
        grid = tk.Frame(parent, bg=BG)
        grid.pack(fill="both", expand=True, padx=10, pady=20)

        for i, (label, cmd) in enumerate(buttons):
            btn = tk.Button(
                grid, text=label, command=cmd, font=("Segoe UI", 11),
                bg=bg_color, fg="white", activebackground=active_color,
                relief="flat", height=3, cursor="hand2",
            )
            btn.grid(row=i // cols, column=i % cols, sticky="nsew", padx=10, pady=10)

        for c in range(cols):
            grid.grid_columnconfigure(c, weight=1)
        for r in range((len(buttons) + cols - 1) // cols):
            grid.grid_rowconfigure(r, weight=1)

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
