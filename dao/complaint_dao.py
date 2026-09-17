from config.db_connector import execute_query
from models.complaint import Complaint


class ComplaintDAO:

    def create(self, complaint: Complaint):
        return execute_query(
            "INSERT INTO complaints (name, contact, message) VALUES (%s, %s, %s)",
            (complaint.name, complaint.contact, complaint.message),
        )

    def get_all(self):
        rows = execute_query("SELECT * FROM complaints ORDER BY created_at DESC", fetch=True)
        return [Complaint.from_row(r) for r in rows]

    def get_open(self):
        rows = execute_query(
            "SELECT * FROM complaints WHERE status = 'open' ORDER BY created_at DESC", fetch=True
        )
        return [Complaint.from_row(r) for r in rows]

    def resolve(self, complaint_id):
        execute_query(
            "UPDATE complaints SET status = 'resolved', resolved_at = NOW() WHERE complaint_id = %s",
            (complaint_id,),
        )
