from dataclasses import dataclass
from typing import Optional


@dataclass
class Admin:
    admin_id: Optional[int]
    username: str
    password_hash: str

    @staticmethod
    def from_row(row: dict) -> "Admin":
        return Admin(
            admin_id=row["admin_id"],
            username=row["username"],
            password_hash=row["password_hash"],
        )
