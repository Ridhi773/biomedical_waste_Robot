from dataclasses import dataclass
from typing import Optional


@dataclass
class Destination:
    destination_id: Optional[int]
    name: str
    qr_code: str
    description: str = ""

    @staticmethod
    def from_row(row: dict) -> "Destination":
        return Destination(
            destination_id=row["destination_id"],
            name=row["name"],
            qr_code=row["qr_code"],
            description=row.get("description") or "",
        )
