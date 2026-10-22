"""Wire arc additive manufacturing context; no strength model or operating limits."""
PROFILE = {
    "name": "waam",
    "label": "Wire arc additive manufacturing (WAAM)",
    "subgroup_col": "build_id",
    "order_col": "build_date",
    "value_col": "uts_mpa",
    "value_label": "Ultimate tensile strength",
    "value_unit": "MPa",
    "parameters": [
        {"column": "arc_current_a", "label": "Arc current", "unit": "A"},
        {"column": "arc_voltage_v", "label": "Arc voltage", "unit": "V"},
        {"column": "wire_feed_rate_m_min", "label": "Wire feed rate", "unit": "m/min"},
        {"column": "travel_speed_mm_s", "label": "Travel speed", "unit": "mm/s"},
        {"column": "shielding_gas_flow_l_min", "label": "Shielding gas flow", "unit": "L/min"},
    ],
}
