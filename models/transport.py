from dataclasses import dataclass
from typing import Optional


@dataclass
class Transport:
    transport_id: Optional[int]
    robot_id: int
    compartment_id: int
    driver_id: Optional[int] = None
    destination_id: Optional[int] = None
    status: str = "pending"   # pending | assigned | in_progress | pickup_verified | completed | cancelled
    requested_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> "Transport":
        return Transport(
            transport_id=row["transport_id"],
            robot_id=row["robot_id"],
            compartment_id=row["compartment_id"],
            driver_id=row.get("driver_id"),
            destination_id=row.get("destination_id"),
            status=row["status"],
            requested_at=str(row.get("requested_at")) if row.get("requested_at") else None,
            started_at=str(row.get("started_at")) if row.get("started_at") else None,
            completed_at=str(row.get("completed_at")) if row.get("completed_at") else None,
        )
