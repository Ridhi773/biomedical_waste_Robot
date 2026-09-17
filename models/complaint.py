from dataclasses import dataclass
from typing import Optional


@dataclass
class Complaint:
    complaint_id: Optional[int]
    message: str
    name: str = ""
    contact: str = ""
    status: str = "open"   # open | resolved
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> "Complaint":
        return Complaint(
            complaint_id=row["complaint_id"],
            message=row["message"],
            name=row.get("name") or "",
            contact=row.get("contact") or "",
            status=row["status"],
            created_at=str(row.get("created_at")) if row.get("created_at") else None,
            resolved_at=str(row.get("resolved_at")) if row.get("resolved_at") else None,
        )
