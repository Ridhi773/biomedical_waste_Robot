from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    location_id: Optional[int]
    name: str
    building: str = ""
    floor: str = ""
    description: str = ""

    @staticmethod
    def from_row(row: dict) -> "Location":
        return Location(
            location_id=row["location_id"],
            name=row["name"],
            building=row.get("building") or "",
            floor=row.get("floor") or "",
            description=row.get("description") or "",
        )
