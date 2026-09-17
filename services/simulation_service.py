"""
Simulates sensor/robot behaviour so the app is demoable without real hardware:
random waste detection, random movement, random battery drain and random faults.
"""

import random

from dao.robot_dao import RobotDAO
from dao.waste_dao import WasteDAO
from dao.compartment_dao import CompartmentDAO
from dao.alert_dao import AlertDAO
from models.alert import Alert
from services.collection_service import CollectionService
from services.tracking_service import TrackingService
from utils.simulation_data import (
    random_weight_kg,
    random_malfunction_message,
    random_route_blocked_message,
    pick_random,
)


class SimulationService:

    def __init__(self):
        self.robot_dao = RobotDAO()
        self.waste_dao = WasteDAO()
        self.compartment_dao = CompartmentDAO()
        self.alert_dao = AlertDAO()
        self.collection_service = CollectionService()
        self.tracking_service = TrackingService()

    def simulate_waste_detection(self, robot_id):
        """Picks one of the robot's own compartments and logs a random waste pickup into it."""
        compartments = self.compartment_dao.get_by_robot(robot_id)
        if not compartments:
            return False, "This robot has no compartments configured."

        compartment = pick_random(compartments)
        locations = self.waste_dao.get_all_locations()
        location = pick_random(locations)
        weight = random_weight_kg()

        ok, msg = self.collection_service.record_collection(
            robot_id=robot_id,
            compartment_id=compartment.compartment_id,
            waste_type_id=compartment.waste_type_id,
            weight_kg=weight,
            location_id=location.location_id if location else None,
        )
        return ok, msg

    def simulate_movement(self, robot_id):
        locations = self.waste_dao.get_all_locations()
        if not locations:
            return False, "No locations configured."
        target = pick_random(locations)
        return self.tracking_service.move_robot_to(robot_id, target.location_id)

    def simulate_random_event(self, robot_id):
        """Randomly raises a malfunction or route-blocked alert (for demo purposes)."""
        event_type = random.choice(["malfunction", "route_blocked"])
        message = (
            random_malfunction_message() if event_type == "malfunction"
            else random_route_blocked_message()
        )
        severity = "high" if event_type == "malfunction" else "medium"

        self.alert_dao.create(Alert(
            alert_id=None,
            robot_id=robot_id,
            alert_type=event_type,
            severity=severity,
            message=message,
        ))

        if event_type == "malfunction":
            self.robot_dao.update_status(robot_id, "error")

        return True, f"{event_type.replace('_', ' ').title()}: {message}"
