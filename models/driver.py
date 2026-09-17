from dataclasses import dataclass
from typing import Optional


@dataclass
class Driver:
    driver_id: Optional[int]
    name: str
    phone: str = ""
    license_no: str = ""
    status: str = "available"   # available | on_duty | off_duty

    @staticmethod
    def from_row(row: dict) -> "Driver":
        return Driver(
            driver_id=row["driver_id"],
            name=row["name"],
            phone=row.get("phone") or "",
            license_no=row.get("license_no") or "",
            status=row["status"],
        )
