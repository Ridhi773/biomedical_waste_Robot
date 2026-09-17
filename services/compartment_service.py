from dao.compartment_dao import CompartmentDAO
from dao.alert_dao import AlertDAO
from models.alert import Alert
from config.config import COMPARTMENT_FULL_THRESHOLD, COMPARTMENT_PARTIAL_THRESHOLD
from utils.validators import is_within_capacity


class CompartmentService:

    def __init__(self):
        self.compartment_dao = CompartmentDAO()
        self.alert_dao = AlertDAO()

    def list_all(self):
        return self.compartment_dao.get_all()

    def list_for_robot(self, robot_id):
        return self.compartment_dao.get_by_robot(robot_id)

    def get(self, compartment_id):
        return self.compartment_dao.get_by_id(compartment_id)

    def _status_for_fill(self, fill_percent):
        if fill_percent >= COMPARTMENT_FULL_THRESHOLD:
            return "full"
        if fill_percent >= COMPARTMENT_PARTIAL_THRESHOLD:
            return "partial"
        return "empty"

    def add_waste(self, compartment_id, weight_kg):
        """
        Adds weight_kg to a compartment's current fill, recalculates status,
        and raises a compartment_full alert if the new level crosses the threshold.
        Returns (success: bool, message: str).
        """
        compartment = self.compartment_dao.get_by_id(compartment_id)
        if compartment is None:
            return False, "Compartment not found."

        if not is_within_capacity(compartment.current_fill_kg, weight_kg, compartment.capacity_kg * 1.15):
            # allow slight overflow tolerance (15%) since real sensors aren't exact,
            # but block wildly invalid entries
            return False, "Weight exceeds compartment capacity by too much."

        new_fill = round(compartment.current_fill_kg + weight_kg, 2)
        new_fill = min(new_fill, compartment.capacity_kg)  # cap the stored value at capacity
        fill_percent = round((new_fill / compartment.capacity_kg) * 100, 1) if compartment.capacity_kg else 0
        new_status = self._status_for_fill(fill_percent)

        self.compartment_dao.update_fill(compartment_id, new_fill, new_status)

        if new_status == "full":
            self.alert_dao.create(Alert(
                alert_id=None,
                robot_id=compartment.robot_id,
                alert_type="compartment_full",
                severity="high",
                message=f"Compartment #{compartment_id} reached {fill_percent}% capacity.",
            ))

        return True, f"Added {weight_kg} kg. Compartment now {fill_percent}% full."

    def empty_compartment(self, compartment_id):
        self.compartment_dao.empty_compartment(compartment_id)
