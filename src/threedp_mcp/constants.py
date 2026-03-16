"""Shared constants for 3DP MCP Server."""

MATERIAL_PROPERTIES = {
    "PLA": {"density": 1.24, "shrinkage": 0.003},
    "PETG": {"density": 1.27, "shrinkage": 0.004},
    "ABS": {"density": 1.04, "shrinkage": 0.007},
    "ASA": {"density": 1.07, "shrinkage": 0.005},
    "TPU": {"density": 1.21, "shrinkage": 0.005},
    "Nylon": {"density": 1.14, "shrinkage": 0.015},
}

ISO_THREAD_TABLE = {
    "M2": {"tap_drill": 1.6, "insert_drill": 3.2, "clearance_drill": 2.4},
    "M2.5": {"tap_drill": 2.05, "insert_drill": 3.5, "clearance_drill": 2.9},
    "M3": {"tap_drill": 2.5, "insert_drill": 4.0, "clearance_drill": 3.4},
    "M4": {"tap_drill": 3.3, "insert_drill": 5.0, "clearance_drill": 4.5},
    "M5": {"tap_drill": 4.2, "insert_drill": 6.0, "clearance_drill": 5.5},
    "M6": {"tap_drill": 5.0, "insert_drill": 7.0, "clearance_drill": 6.6},
    "M8": {"tap_drill": 6.8, "insert_drill": 9.5, "clearance_drill": 8.4},
    "M10": {"tap_drill": 8.5, "insert_drill": 12.0, "clearance_drill": 10.5},
}
