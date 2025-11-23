from rooms.models import Room


def get_rooms_with_on_off_heating_control_data() -> list[dict]:
    """Return useful data for on/off heating control"""
    return list(
        Room.objects.filter(
            heating_control_mode=Room.HeatingControlMode.ONOFF,
            radiator__isnull=False,
            requested_heating_state__in=[
                Room.RequestedHeatingState.OFF,
                Room.RequestedHeatingState.ON,
            ],
        ).values(
            "radiator__id",
            "radiator__power",
            "radiator__importance",
            "radiator__requested_state",
            "requested_heating_state",
        )
    )
