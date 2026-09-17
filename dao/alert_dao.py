from config.db_connector import execute_query
from models.alert import Alert


class AlertDAO:

    def get_all(self):
        rows = execute_query("SELECT * FROM alerts ORDER BY created_at DESC", fetch=True)
        return [Alert.from_row(r) for r in rows]

    def get_unresolved(self):
        rows = execute_query(
            "SELECT * FROM alerts WHERE resolved = FALSE ORDER BY created_at DESC", fetch=True
        )
        return [Alert.from_row(r) for r in rows]

    def create(self, alert: Alert):
        return execute_query(
            "INSERT INTO alerts (robot_id, alert_type, severity, message) VALUES (%s, %s, %s, %s)",
            (alert.robot_id, alert.alert_type, alert.severity, alert.message),
        )

    def resolve(self, alert_id):
        execute_query(
            "UPDATE alerts SET resolved = TRUE, resolved_at = NOW() WHERE alert_id = %s",
            (alert_id,),
        )

    def get_with_robot_names(self):
        query = """
            SELECT a.alert_id, a.alert_type, a.severity, a.message,
                   a.created_at, a.resolved, a.resolved_at,
                   r.name AS robot_name
            FROM alerts a
            JOIN robots r ON a.robot_id = r.robot_id
            ORDER BY a.resolved ASC, a.created_at DESC
        """
        return execute_query(query, fetch=True)
