from config.db_connector import execute_query
from models.qr_verification import QRVerification


class QRVerificationDAO:

    def create(self, verification: QRVerification):
        return execute_query(
            "INSERT INTO qr_verifications (transport_id, stage, scanned_code, expected_code, result) "
            "VALUES (%s, %s, %s, %s, %s)",
            (verification.transport_id, verification.stage, verification.scanned_code,
             verification.expected_code, verification.result),
        )

    def get_by_transport(self, transport_id):
        rows = execute_query(
            "SELECT * FROM qr_verifications WHERE transport_id = %s ORDER BY verified_at DESC",
            (transport_id,), fetch=True,
        )
        return [QRVerification.from_row(r) for r in rows]

    def get_with_details(self):
        """Joined audit-log view for the QR Verification Log screen."""
        query = """
            SELECT q.qr_verification_id, q.stage, q.scanned_code, q.expected_code,
                   q.result, q.verified_at,
                   t.transport_id, r.name AS robot_name
            FROM qr_verifications q
            JOIN transports t ON q.transport_id = t.transport_id
            JOIN robots r ON t.robot_id = r.robot_id
            ORDER BY q.verified_at DESC
        """
        return execute_query(query, fetch=True)
