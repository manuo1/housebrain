from actuators.models import Radiator


def get_radiators_state_in_database() -> list[dict]:
    """
    Return the minimum info needed for driver synchronization:
    - id (int)
    - control_pin (int)
    - requested_state (str)
    - actual_state (str)
    - error (str | None)
    """
    return list(
        Radiator.objects.values(
            "id",
            "control_pin",
            "requested_state",
            "actual_state",
            "error",
        )
    )
