from config.db_connector import execute_query
from models.admin import Admin


class AdminDAO:

    def get_by_username(self, username):
        row = execute_query("SELECT * FROM admin WHERE username = %s", (username,), fetchone=True)
        return Admin.from_row(row) if row else None
