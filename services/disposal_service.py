"""Final step of the flow: confirming disposal and freeing up the compartment."""

from dao.transport_dao import TransportDAO
from dao.qr_verification_dao import QRVerificationDAO
from dao.driver_dao import DriverDAO
from services.compartment_service import CompartmentService


class DisposalService:

    def __init__(self):
        self.transport_dao = TransportDAO()
        self.qr_verification_dao = QRVerificationDAO()
        self.driver_dao = DriverDAO()
        self.compartment_service = CompartmentService()

    def confirm_disposal(self, transport_id):
        """
        Only allowed once the destination scan for this transport has
        actually matched - otherwise the driver could skip verification.
        """
        transport = self.transport_dao.get_by_id(transport_id)
        if transport is None:
            return False, "Transport request not found."
        if transport.destination_id is None:
            return False, "Verify the destination QR before confirming disposal."

        verifications = self.qr_verification_dao.get_by_transport(transport_id)
        destination_matches = [
            v for v in verifications if v.stage == "destination" and v.result == "match"
        ]
        if not destination_matches:
            return False, "No successful destination verification found for this transport."

        self.transport_dao.complete(transport_id)
        self.compartment_service.empty_compartment(transport.compartment_id)
        if transport.driver_id is not None:
                self.driver_dao.update_status(transport.driver_id, "available")

        return True, "Disposal confirmed - compartment reset and ready for reuse."
