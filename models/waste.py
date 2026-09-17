from dataclasses import dataclass
from typing import Optional


@dataclass
class WasteType:
    waste_type_id: Optional[int]
    name: str
    category: str = "general"    # sharps | infectious | pathological | chemical | general
    hazard_level: str = "medium" # low | medium | high | critical

    @staticmethod
    def from_row(row: dict) -> "WasteType":
        return WasteType(
            waste_type_id=row["waste_type_id"],
            name=row["name"],
            category=row["category"],
            hazard_level=row["hazard_level"],
        )
