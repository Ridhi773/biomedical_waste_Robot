from dataclasses import dataclass
from typing import Optional


@dataclass
class Compartment:
    compartment_id: Optional[int]
    robot_id: int
    waste_type_id: int
    capacity_kg: float
    current_fill_kg: float = 0.0
    status: str = "empty"   # empty | partial | full
    qr_code: str = ""

    @property
    def fill_percent(self) -> float:
        if self.capacity_kg <= 0:
            return 0.0
        return round((self.current_fill_kg / self.capacity_kg) * 100, 1)

    @staticmethod
    def from_row(row: dict) -> "Compartment":
        return Compartment(
            compartment_id=row["compartment_id"],
            robot_id=row["robot_id"],
            waste_type_id=row["waste_type_id"],
            capacity_kg=float(row["capacity_kg"]),
            current_fill_kg=float(row["current_fill_kg"]),
            status=row["status"],
            qr_code=row.get("qr_code") or "",
        )
