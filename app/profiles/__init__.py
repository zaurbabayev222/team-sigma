"""Explicit process registry, usable from the source checkout or flat Connect bundle."""
from .lpbf import PROFILE as LPBF
from .waam import PROFILE as WAAM
from .ebpbf import PROFILE as EBPBF
from .laser_ded import PROFILE as LASER_DED

PROFILES = {profile['name']: profile for profile in (LPBF, WAAM, EBPBF, LASER_DED)}
SCENARIOS = ('stable_capable', 'stable_incapable', 'unstable_shift')
DATASETS = {name: tuple((name + '_' if name != 'lpbf' else '') + scenario for scenario in SCENARIOS) + (name + '_inspection_demo',)
            for name in PROFILES}


def get_profile(process_type):
    """Unknown process IDs never silently fall back to another technology."""
    try:
        return PROFILES[process_type]
    except KeyError:
        raise ValueError('unknown process_type; choose ' + ', '.join(PROFILES)) from None
