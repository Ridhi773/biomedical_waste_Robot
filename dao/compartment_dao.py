from config.db_connector import execute_query
from models.compartment import Compartment


class CompartmentDAO:

    def get_all(self):
        rows = execute_query("SELECT * FROM compartments ORDER BY compartment_id", fetch=True)
        return [Compartment.from_row(r) for r in rows]

    def get_by_robot(self, robot_id):
        rows = execute_query(
            "SELECT * FROM compartments WHERE robot_id = %s ORDER BY compartment_id",
            (robot_id,), fetch=True,
        )
        return [Compartment.from_row(r) for r in rows]

    def get_by_id(self, compartment_id):
        row = execute_query(
            "SELECT * FROM compartments WHERE compartment_id = %s", (compartment_id,), fetchone=True
        )
        return Compartment.from_row(row) if row else None

    def create(self, compartment: Compartment):
        return execute_query(
            "INSERT INTO compartments (robot_id, waste_type_id, capacity_kg, current_fill_kg, status, qr_code) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (compartment.robot_id, compartment.waste_type_id, compartment.capacity_kg,
             compartment.current_fill_kg, compartment.status, compartment.qr_code),
        )

    def get_by_qr_code(self, qr_code):
        row = execute_query(
            "SELECT * FROM compartments WHERE qr_code = %s", (qr_code,), fetchone=True
        )
        return Compartment.from_row(row) if row else None

    def update_fill(self, compartment_id, current_fill_kg, status):
        execute_query(
            "UPDATE compartments SET current_fill_kg = %s, status = %s WHERE compartment_id = %s",
            (current_fill_kg, status, compartment_id),
        )

    def empty_compartment(self, compartment_id):
        execute_query(
            "UPDATE compartments SET current_fill_kg = 0, status = 'empty' WHERE compartment_id = %s",
            (compartment_id,),
        )
