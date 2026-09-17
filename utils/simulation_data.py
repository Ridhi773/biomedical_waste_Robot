"""
Fake-but-plausible data generators, since there's no physical robot/sensor
feeding real readings yet. Used by simulation_service.
"""

import random
from config.config import SIM_WEIGHT_RANGE_KG

MALFUNCTION_MESSAGES = [
    "Arm actuator response delayed",
    "Sensor calibration drift detected",
    "Unexpected obstacle in path",
    "Compartment lid sensor unresponsive",
    "Navigation signal lost momentarily",
]

ROUTE_BLOCKED_MESSAGES = [
    "Corridor blocked by equipment cart",
    "Door access denied at checkpoint",
    "Elevator unavailable on scheduled route",
]


def random_weight_kg():
    lo, hi = SIM_WEIGHT_RANGE_KG
    return round(random.uniform(lo, hi), 2)


def random_malfunction_message():
    return random.choice(MALFUNCTION_MESSAGES)


def random_route_blocked_message():
    return random.choice(ROUTE_BLOCKED_MESSAGES)


def pick_random(items):
    return random.choice(items) if items else None
