from config.db_connector import execute_query
from models.waste import WasteType
from models.location import Location


class WasteDAO:

    def get_all_waste_types(self):
        rows = execute_query("SELECT * FROM waste_types ORDER BY waste_type_id", fetch=True)
        return [WasteType.from_row(r) for r in rows]

    def get_waste_type_by_id(self, waste_type_id):
        row = execute_query(
            "SELECT * FROM waste_types WHERE waste_type_id = %s", (waste_type_id,), fetchone=True
        )
        return WasteType.from_row(row) if row else None

    def create_waste_type(self, waste_type: WasteType):
        return execute_query(
            "INSERT INTO waste_types (name, category, hazard_level) VALUES (%s, %s, %s)",
            (waste_type.name, waste_type.category, waste_type.hazard_level),
        )

    def get_all_locations(self):
        rows = execute_query("SELECT * FROM locations ORDER BY location_id", fetch=True)
        return [Location.from_row(r) for r in rows]

    def get_location_by_id(self, location_id):
        row = execute_query(
            "SELECT * FROM locations WHERE location_id = %s", (location_id,), fetchone=True
        )
        return Location.from_row(row) if row else None
