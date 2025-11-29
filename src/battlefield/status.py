from enum import Enum

"""
FYI:

NVS (Non-volatile status): status that remains in the Pokemon even when you take it out from the battle.
VS (volatile status): temporary status that fades away once you remove the Pokemon from the battlefield.
"""

class NVStatus(str, Enum):
    NONE = "not affected by any condition"
    BURNT = "burnt"
    FROZEN = "frozen"
    PARALIZED = "paralized"
    POISONED = "poisoned"
    ASLEEP = "asleep"


class VStatus(str, Enum):
    NONE = "not affected by any non-volatile status"
    CONFUSED = "confused"


def set_nvstatus_from_api(input: str) -> NVStatus:
    if input == "paralysis":
        return NVStatus.PARALIZED
    elif input == "sleep":
        return NVStatus.ASLEEP
    elif input == "freeze":
        return NVStatus.FROZEN
    elif input == "burn":
        return NVStatus.BURNT
    elif input == "poison":
        return NVStatus.POISONED
    else:
        return NVStatus.NONE