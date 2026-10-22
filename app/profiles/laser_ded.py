"""Powder-fed laser DED context; does not cover every DED feedstock/energy source."""
PROFILE = {
    'name': 'laser_ded', 'label': 'Powder-fed laser directed energy deposition (laser DED)',
    'short_label': 'Laser DED',
    'subgroup_col': 'build_id', 'order_col': 'build_date', 'value_col': 'uts_mpa',
    'value_label': 'Ultimate tensile strength', 'value_unit': 'MPa',
    'parameters': [
        {'column': 'laser_power_w', 'label': 'Laser power', 'unit': 'W'},
        {'column': 'powder_feed_rate_g_min', 'label': 'Powder feed rate', 'unit': 'g/min'},
        {'column': 'travel_speed_mm_s', 'label': 'Travel speed', 'unit': 'mm/s'},
        {'column': 'shielding_gas_flow_l_min', 'label': 'Shielding gas flow', 'unit': 'L/min'},
        {'column': 'standoff_distance_mm', 'label': 'Standoff distance', 'unit': 'mm'},
    ],
}
