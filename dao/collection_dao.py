from config.db_connector import execute_query
from models.collection import Collection


class CollectionDAO:

    def get_all(self):
        rows = execute_query(
            "SELECT * FROM collections ORDER BY collected_at DESC", fetch=True
        )
        return [Collection.from_row(r) for r in rows]

    def get_by_robot(self, robot_id):
        rows = execute_query(
            "SELECT * FROM collections WHERE robot_id = %s ORDER BY collected_at DESC",
            (robot_id,), fetch=True,
        )
        return [Collection.from_row(r) for r in rows]

    def create(self, collection: Collection):
        return execute_query(
            "INSERT INTO collections (robot_id, compartment_id, location_id, waste_type_id, weight_kg) "
            "VALUES (%s, %s, %s, %s, %s)",
            (collection.robot_id, collection.compartment_id, collection.location_id,
             collection.waste_type_id, collection.weight_kg),
        )

    def get_with_details(self):
        """Joined view used by the collection history screen."""
        query = """
            SELECT c.collection_id, c.weight_kg, c.collected_at,
                   r.name AS robot_name,
                   w.name AS waste_name, w.category AS waste_category,
                   l.name AS location_name
            FROM collections c
            JOIN robots r ON c.robot_id = r.robot_id
            JOIN waste_types w ON c.waste_type_id = w.waste_type_id
            LEFT JOIN locations l ON c.location_id = l.location_id
            ORDER BY c.collected_at DESC
        """
        return execute_query(query, fetch=True)
