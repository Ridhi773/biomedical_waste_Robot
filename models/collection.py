from dataclasses import dataclass
from typing import Optional


@dataclass
class Collection:
    collection_id: Optional[int]
    robot_id: int
    compartment_id: int
    waste_type_id: int
    weight_kg: float
    location_id: Optional[int] = None
    collected_at: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> "Collection":
        return Collection(
            collection_id=row["collection_id"],
            robot_id=row["robot_id"],
            compartment_id=row["compartment_id"],
            waste_type_id=row["waste_type_id"],
            weight_kg=float(row["weight_kg"]),
            location_id=row.get("location_id"),
            collected_at=str(row.get("collected_at")) if row.get("collected_at") else None,
        )
