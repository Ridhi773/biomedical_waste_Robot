"""
Implements the "scan QR -> match/mismatch" step of the flow, both at the
robot compartment (pickup) and at the disposal site (destination).
"""

from dao.transport_dao import TransportDAO
from dao.compartment_dao import CompartmentDAO
from dao.destination_dao import DestinationDAO
from dao.qr_verification_dao import QRVerificationDAO
from dao.alert_dao import AlertDAO
from models.qr_verification import QRVerification
from models.alert import Alert
from utils.qr_utils import codes_match


class QRService:

    def __init__(self):
        self.transport_dao = TransportDAO()
        self.compartment_dao = CompartmentDAO()
        self.destination_dao = DestinationDAO()
        self.qr_verification_dao = QRVerificationDAO()
        self.alert_dao = AlertDAO()

    def verify_pickup(self, transport_id, scanned_code):
        """
        Driver scans the compartment's QR before it's allowed to be dumped.
        MATCH  -> access authorized, dumping confirmed, transport moves to 'pickup_verified'.
        MISMATCH -> access denied, an alert is raised, transport status is unchanged.
        """
        transport = self.transport_dao.get_by_id(transport_id)
        if transport is None:
            return False, "Transport request not found."
        if transport.status != "in_progress":
            return False, "Transport must be started before a pickup scan."

        compartment = self.compartment_dao.get_by_id(transport.compartment_id)
        expected_code = compartment.qr_code
        result = "match" if codes_match(scanned_code, expected_code) else "mismatch"

        self.qr_verification_dao.create(QRVerification(
            qr_verification_id=None,
            transport_id=transport_id,
            stage="pickup",
            scanned_code=scanned_code,
            expected_code=expected_code,
            result=result,
        ))

        if result == "match":
            self.transport_dao.mark_pickup_verified(transport_id)
            return True, "Access authorized - dumping confirmed."

        self.alert_dao.create(Alert(
            alert_id=None,
            robot_id=transport.robot_id,
            alert_type="qr_mismatch",
            severity="high",
            message=f"Pickup QR mismatch on transport #{transport_id} - access denied.",
        ))
        return False, "Access denied - scanned code does not match this compartment."

    def verify_destination(self, transport_id, destination_id, scanned_code):
        """
        Driver scans the destination's QR at the disposal site.
        MATCH -> destination verified, ready for final disposal confirmation.
        MISMATCH -> alert raised, disposal is blocked.
        """
        transport = self.transport_dao.get_by_id(transport_id)
        if transport is None:
            return False, "Transport request not found."
        if transport.status != "pickup_verified":
            return False, "Pickup must be verified before a destination scan."

        destination = self.destination_dao.get_by_id(destination_id)
        if destination is None:
            return False, "Destination not found."
        expected_code = destination.qr_code
        result = "match" if codes_match(scanned_code, expected_code) else "mismatch"

        self.qr_verification_dao.create(QRVerification(
            qr_verification_id=None,
            transport_id=transport_id,
            stage="destination",
            scanned_code=scanned_code,
            expected_code=expected_code,
            result=result,
        ))

        if result == "match":
            self.transport_dao.set_destination(transport_id, destination_id)
            return True, "Destination verified - ready to confirm disposal."

        self.alert_dao.create(Alert(
            alert_id=None,
            robot_id=transport.robot_id,
            alert_type="qr_mismatch",
            severity="critical",
            message=f"Destination QR mismatch on transport #{transport_id} - disposal blocked.",
        ))
        return False, "Access denied - this does not look like the assigned destination."

    def list_log(self):
        return self.qr_verification_dao.get_with_details()
