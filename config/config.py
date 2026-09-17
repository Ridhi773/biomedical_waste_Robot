"""
Central configuration for the Biomedical Waste Robot system.
Edit DB_CONFIG to match your local MySQL Server setup.
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "mysql password",   # <-- change this
    "database": "biomedical_waste_robot",
}

# Thresholds used across services
COMPARTMENT_FULL_THRESHOLD = 90.0     # % fill considered "full"
COMPARTMENT_PARTIAL_THRESHOLD = 10.0  # % fill considered "partial" (below this = empty)
LOW_BATTERY_THRESHOLD = 20.0          # % battery considered "low"

# Simulation tuning
SIM_BATTERY_DRAIN_PER_MOVE = 3.0      # % battery lost per simulated move
SIM_WEIGHT_RANGE_KG = (0.1, 4.5)      # min/max weight per simulated waste detection
