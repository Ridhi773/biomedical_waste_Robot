from dataclasses import dataclass
from typing import Optional


@dataclass
class Alert:
    alert_id: Optional[int]
    robot_id: int
    alert_type: str          # compartment_full | low_battery | malfunction | route_blocked
    severity: str             # low | medium | high | critical
    message: str
    created_at: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> "Alert":
        return Alert(
            alert_id=row["alert_id"],
            robot_id=row["robot_id"],
            alert_type=row["alert_type"],
            severity=row["severity"],
            message=row["message"],
            created_at=str(row.get("created_at")) if row.get("created_at") else None,
            resolved=bool(row.get("resolved")),
            resolved_at=str(row.get("resolved_at")) if row.get("resolved_at") else None,
        )
