from config.db_connector import execute_query
from models.destination import Destination


class DestinationDAO:

    def get_all(self):
        rows = execute_query("SELECT * FROM destinations ORDER BY name", fetch=True)
        return [Destination.from_row(r) for r in rows]

    def get_by_id(self, destination_id):
        row = execute_query(
            "SELECT * FROM destinations WHERE destination_id = %s", (destination_id,), fetchone=True
        )
        return Destination.from_row(row) if row else None
