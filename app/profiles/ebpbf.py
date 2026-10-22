"""Electron beam powder bed fusion context; illustrative values, no operating limits."""
PROFILE = {
    'name': 'ebpbf', 'label': 'Electron beam powder bed fusion (EB-PBF)',
    'short_label': 'EB-PBF',
    'subgroup_col': 'build_id', 'order_col': 'build_date', 'value_col': 'uts_mpa',
    'value_label': 'Ultimate tensile strength', 'value_unit': 'MPa',
    'parameters': [
        {'column': 'beam_current_ma', 'label': 'Beam current', 'unit': 'mA'},
        {'column': 'accelerating_voltage_kv', 'label': 'Accelerating voltage', 'unit': 'kV'},
        {'column': 'scan_speed_mm_s', 'label': 'Scan speed', 'unit': 'mm/s'},
        {'column': 'preheat_temperature_c', 'label': 'Preheat temperature', 'unit': 'deg C'},
        {'column': 'chamber_pressure_pa', 'label': 'Chamber pressure', 'unit': 'Pa'},
    ],
}
