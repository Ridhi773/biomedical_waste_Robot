def is_positive_number(value) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def is_non_negative_number(value) -> bool:
    try:
        return float(value) >= 0
    except (TypeError, ValueError):
        return False


def is_non_empty_string(value) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def is_valid_battery_level(value) -> bool:
    try:
        v = float(value)
        return 0 <= v <= 100
    except (TypeError, ValueError):
        return False


def is_within_capacity(current_fill_kg, add_kg, capacity_kg) -> bool:
    try:
        return (float(current_fill_kg) + float(add_kg)) <= float(capacity_kg) + 0.001
    except (TypeError, ValueError):
        return False
