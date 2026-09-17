from dao.robot_dao import RobotDAO
from dao.waste_dao import WasteDAO
from config.config import LOW_BATTERY_THRESHOLD


class RobotService:

    def __init__(self):
        self.robot_dao = RobotDAO()
        self.waste_dao = WasteDAO()

    def list_robots(self):
        return self.robot_dao.get_all()

    def get_robot(self, robot_id):
        return self.robot_dao.get_by_id(robot_id)

    def get_robot_location_name(self, robot):
        if not robot.current_location_id:
            return "Unknown"
        loc = self.waste_dao.get_location_by_id(robot.current_location_id)
        return loc.name if loc else "Unknown"

    def set_status(self, robot_id, status):
        self.robot_dao.update_status(robot_id, status)

    def is_battery_low(self, robot):
        return robot.battery_level <= LOW_BATTERY_THRESHOLD
