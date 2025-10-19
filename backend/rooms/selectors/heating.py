from rooms.models import Room


def get_rooms_with_on_off_heating_control_data() -> list[dict]:
    """Return useful data for on/off heating control"""
    return list(
        Room.objects.filter(
            heating_control_mode=Room.HeatingControlMode.ONOFF,
            radiator__isnull=False,
            current_on_off_state__in=[
                Room.CurrentHeatingState.OFF,
                Room.CurrentHeatingState.ON,
            ],
        ).values("radiator__id", "current_on_off_state")
    )
