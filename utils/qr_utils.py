"""
QR-code helpers. There's no physical scanner here, so "scanning" in the GUI
means the driver picks/enters a code that gets compared to the expected one
stored against the compartment or destination - this module just generates
those codes and does the comparison.
"""

import uuid


def generate_code(prefix="CODE"):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def codes_match(scanned_code, expected_code):
    if not scanned_code or not expected_code:
        return False
    return scanned_code.strip().upper() == expected_code.strip().upper()
