from config.db_connector import execute_query
from models.transport import Transport


class TransportDAO:

    def get_all(self):
        rows = execute_query("SELECT * FROM transports ORDER BY requested_at DESC", fetch=True)
        return [Transport.from_row(r) for r in rows]

    def get_by_status(self, status):
        rows = execute_query(
            "SELECT * FROM transports WHERE status = %s ORDER BY requested_at DESC",
            (status,), fetch=True,
        )
        return [Transport.from_row(r) for r in rows]

    def get_by_id(self, transport_id):
        row = execute_query(
            "SELECT * FROM transports WHERE transport_id = %s", (transport_id,), fetchone=True
        )
        return Transport.from_row(row) if row else None

    def create(self, transport: Transport):
        return execute_query(
            "INSERT INTO transports (robot_id, compartment_id, status) VALUES (%s, %s, %s)",
            (transport.robot_id, transport.compartment_id, transport.status),
        )

    def assign_driver(self, transport_id, driver_id):
        execute_query(
            "UPDATE transports SET driver_id = %s, status = 'assigned' WHERE transport_id = %s",
            (driver_id, transport_id),
        )

    def start(self, transport_id):
        execute_query(
            "UPDATE transports SET status = 'in_progress', started_at = NOW() WHERE transport_id = %s",
            (transport_id,),
        )

    def mark_pickup_verified(self, transport_id):
        execute_query(
            "UPDATE transports SET status = 'pickup_verified' WHERE transport_id = %s",
            (transport_id,),
        )

    def set_destination(self, transport_id, destination_id):
        execute_query(
            "UPDATE transports SET destination_id = %s WHERE transport_id = %s",
            (destination_id, transport_id),
        )

    def complete(self, transport_id):
        execute_query(
            "UPDATE transports SET status = 'completed', completed_at = NOW() WHERE transport_id = %s",
            (transport_id,),
        )

    def get_with_details(self):
        """Joined view used by the transport requests / scanner screens."""
        query = """
            SELECT t.transport_id, t.status, t.requested_at, t.started_at, t.completed_at,
                   r.name AS robot_name,
                   c.compartment_id, c.qr_code AS compartment_qr,
                   d.name AS driver_name,
                   dest.name AS destination_name
            FROM transports t
            JOIN robots r ON t.robot_id = r.robot_id
            JOIN compartments c ON t.compartment_id = c.compartment_id
            LEFT JOIN drivers d ON t.driver_id = d.driver_id
            LEFT JOIN destinations dest ON t.destination_id = dest.destination_id
            ORDER BY t.requested_at DESC
        """
        return execute_query(query, fetch=True)
