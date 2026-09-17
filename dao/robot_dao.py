from config.db_connector import execute_query
from models.robot import Robot


class RobotDAO:

    def get_all(self):
        rows = execute_query("SELECT * FROM robots ORDER BY robot_id", fetch=True)
        return [Robot.from_row(r) for r in rows]

    def get_by_id(self, robot_id):
        row = execute_query("SELECT * FROM robots WHERE robot_id = %s", (robot_id,), fetchone=True)
        return Robot.from_row(row) if row else None

    def create(self, robot: Robot):
        return execute_query(
            "INSERT INTO robots (name, status, battery_level, current_location_id) "
            "VALUES (%s, %s, %s, %s)",
            (robot.name, robot.status, robot.battery_level, robot.current_location_id),
        )

    def update_status(self, robot_id, status):
        execute_query("UPDATE robots SET status = %s WHERE robot_id = %s", (status, robot_id))

    def update_battery(self, robot_id, battery_level):
        execute_query(
            "UPDATE robots SET battery_level = %s WHERE robot_id = %s",
            (battery_level, robot_id),
        )

    def update_location(self, robot_id, location_id):
        execute_query(
            "UPDATE robots SET current_location_id = %s WHERE robot_id = %s",
            (location_id, robot_id),
        )

    def delete(self, robot_id):
        execute_query("DELETE FROM robots WHERE robot_id = %s", (robot_id,))
