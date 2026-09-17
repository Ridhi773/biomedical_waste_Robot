from dataclasses import dataclass
from typing import Optional


@dataclass
class Robot:
    robot_id: Optional[int]
    name: str
    status: str = "idle"                 # idle | collecting | charging | error
    battery_level: float = 100.0
    current_location_id: Optional[int] = None
    last_updated: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> "Robot":
        return Robot(
            robot_id=row["robot_id"],
            name=row["name"],
            status=row["status"],
            battery_level=float(row["battery_level"]),
            current_location_id=row.get("current_location_id"),
            last_updated=str(row.get("last_updated")) if row.get("last_updated") else None,
        )
