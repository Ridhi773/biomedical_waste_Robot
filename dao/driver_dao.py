from config.db_connector import execute_query
from models.driver import Driver


class DriverDAO:

    def get_all(self):
        rows = execute_query("SELECT * FROM drivers ORDER BY name", fetch=True)
        return [Driver.from_row(r) for r in rows]

    def get_available(self):
        rows = execute_query(
            "SELECT * FROM drivers WHERE status = 'available' ORDER BY name", fetch=True
        )
        return [Driver.from_row(r) for r in rows]

    def get_by_id(self, driver_id):
        row = execute_query("SELECT * FROM drivers WHERE driver_id = %s", (driver_id,), fetchone=True)
        return Driver.from_row(row) if row else None

    def update_status(self, driver_id, status):
        execute_query("UPDATE drivers SET status = %s WHERE driver_id = %s", (status, driver_id))
