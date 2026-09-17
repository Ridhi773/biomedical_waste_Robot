from dao.robot_dao import RobotDAO
from dao.waste_dao import WasteDAO
from dao.alert_dao import AlertDAO
from models.alert import Alert
from config.config import LOW_BATTERY_THRESHOLD, SIM_BATTERY_DRAIN_PER_MOVE


class TrackingService:
    """Tracks and updates robot location + battery as it 'moves' around the facility."""

    def __init__(self):
        self.robot_dao = RobotDAO()
        self.waste_dao = WasteDAO()
        self.alert_dao = AlertDAO()

    def get_all_locations(self):
        return self.waste_dao.get_all_locations()

    def move_robot_to(self, robot_id, location_id):
        """Moves a robot to a specific location and drains a bit of battery."""
        robot = self.robot_dao.get_by_id(robot_id)
        if robot is None:
            return False, "Robot not found."

        self.robot_dao.update_location(robot_id, location_id)

        new_battery = max(0.0, round(robot.battery_level - SIM_BATTERY_DRAIN_PER_MOVE, 1))
        self.robot_dao.update_battery(robot_id, new_battery)

        if new_battery <= LOW_BATTERY_THRESHOLD:
            self.alert_dao.create(Alert(
                alert_id=None,
                robot_id=robot_id,
                alert_type="low_battery",
                severity="medium" if new_battery > 10 else "critical",
                message=f"Battery at {new_battery}%. Return to charging bay recommended.",
            ))

        return True, f"Robot moved. Battery now {new_battery}%."

    def send_to_charging(self, robot_id, charging_location_id):
        self.robot_dao.update_location(robot_id, charging_location_id)
        self.robot_dao.update_status(robot_id, "charging")
        self.robot_dao.update_battery(robot_id, 100.0)
