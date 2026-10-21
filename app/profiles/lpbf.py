"""Process profile for laser powder bed fusion (LPBF).

Everything specific to one printing process lives in a file like this one.
Adding a process later = add one more file like this; qc.py does not change.
"""
PROFILE = {
    "name": "lpbf",
    "label": "Laser powder bed fusion (LPBF)",
    "subgroup_col": "build_id",
    "order_col": "build_date",
    "value_col": "uts_mpa",
    "value_label": "Ultimate tensile strength",
    "value_unit": "MPa",
    # Optional process parameters: shown next to flagged builds, never used in the statistics.
    "parameters": [
        {"column": "chamber_oxygen_ppm", "label": "Chamber oxygen", "unit": "ppm"},
        {"column": "powder_reuse_count", "label": "Powder reuse count", "unit": "times"},
        {"column": "laser_power_w", "label": "Laser power", "unit": "W"},
    ],
}
