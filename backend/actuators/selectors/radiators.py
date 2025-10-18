from actuators.models import Radiator


def get_radiators_state_in_database() -> list[dict]:
    """
    Return the minimum info needed for driver synchronization:
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


def get_radiators_data_for_load_shedding() -> list[dict]:
    """
    Return the minimum info needed for load shedding
    """
    return list(
        Radiator.objects.filter(actual_state=Radiator.ActualState.ON, power__gt=0)
        .order_by("-importance", "-power")
        .values("id", "power", "importance")
    )
