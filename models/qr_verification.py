from dataclasses import dataclass
from typing import Optional


@dataclass
class QRVerification:
    qr_verification_id: Optional[int]
    transport_id: int
    stage: str          # pickup | destination
    scanned_code: str
    expected_code: str
    result: str          # match | mismatch
    verified_at: Optional[str] = None

    @staticmethod
    def from_row(row: dict) -> "QRVerification":
        return QRVerification(
            qr_verification_id=row["qr_verification_id"],
            transport_id=row["transport_id"],
            stage=row["stage"],
            scanned_code=row["scanned_code"],
            expected_code=row["expected_code"],
            result=row["result"],
            verified_at=str(row.get("verified_at")) if row.get("verified_at") else None,
        )
