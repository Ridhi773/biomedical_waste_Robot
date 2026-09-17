"""
Handles the transport-request part of the flow: a full compartment becomes
a transport request, a driver gets assigned, and the driver starts the run.
"""

from dao.transport_dao import TransportDAO
from dao.compartment_dao import CompartmentDAO
from dao.driver_dao import DriverDAO
from models.transport import Transport


class TransportService:

    def __init__(self):
        self.transport_dao = TransportDAO()
        self.compartment_dao = CompartmentDAO()
        self.driver_dao = DriverDAO()

    def create_request(self, robot_id, compartment_id):
        """Only compartments already marked 'full' can be requested for transport."""
        compartment = self.compartment_dao.get_by_id(compartment_id)
        if compartment is None:
            return False, "Compartment not found."
        if compartment.status != "full":
            return False, "Compartment is not full yet - nothing to transport."

        self.transport_dao.create(Transport(
            transport_id=None,
            robot_id=robot_id,
            compartment_id=compartment_id,
        ))
        return True, "Transport request created."

    def list_with_details(self):
        return self.transport_dao.get_with_details()

    def list_by_status(self, status):
        return self.transport_dao.get_by_status(status)

    def get(self, transport_id):
        return self.transport_dao.get_by_id(transport_id)

    def list_available_drivers(self):
        return self.driver_dao.get_available()

    def assign_driver(self, transport_id, driver_id):
        transport = self.transport_dao.get_by_id(transport_id)
        if transport is None:
            return False, "Transport request not found."
        if transport.status != "pending":
            return False, "Only pending requests can be assigned a driver."

        self.transport_dao.assign_driver(transport_id, driver_id)
        self.driver_dao.update_status(driver_id, "on_duty")
        return True, "Driver assigned."

    def start_transport(self, transport_id):
        transport = self.transport_dao.get_by_id(transport_id)
        if transport is None:
            return False, "Transport request not found."
        if transport.status != "assigned":
            return False, "Assign a driver before starting the transport."

        self.transport_dao.start(transport_id)
        return True, "Transport started - ready for pickup QR scan."
