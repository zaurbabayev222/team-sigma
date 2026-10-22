"""Explicit process registry, usable from the source checkout or flat Connect bundle."""
from .lpbf import PROFILE as LPBF
from .waam import PROFILE as WAAM

PROFILES = {profile['name']: profile for profile in (LPBF, WAAM)}
SCENARIOS = ('stable_capable', 'stable_incapable', 'unstable_shift')
DATASETS = {
    'lpbf': SCENARIOS,
    'waam': tuple('waam_' + scenario for scenario in SCENARIOS),
}


def get_profile(process_type):
    """Unknown process IDs never silently fall back to another technology."""
    try:
        return PROFILES[process_type]
    except KeyError:
        raise ValueError('unknown process_type; choose lpbf or waam') from None
