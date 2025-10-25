from actuators.models import Radiator


def get_radiators_data_for_hardware_synchronization() -> list[dict]:
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


def get_radiators_data_for_on_off_heating_control(id_list: list[int]) -> list[dict]:
    """
    Return the minimum radiators info needed for the On/Off heating mode control"""
    return list(
        Radiator.objects.filter(id__in=id_list).values(
            "id",
            "requested_state",
            "power",
            "importance",
        )
    )
