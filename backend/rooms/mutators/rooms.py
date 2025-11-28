from rooms.models import Room


def update_room_heating_fields(
    room_id: int,
    heating_control_mode: Room.HeatingControlMode,
    temperature_setpoint: float | None,
    requested_heating_state: Room.RequestedHeatingState,
) -> bool:
    updated = Room.objects.filter(id=room_id).update(
        heating_control_mode=heating_control_mode,
        temperature_setpoint=temperature_setpoint,
        requested_heating_state=requested_heating_state,
    )

    return updated == 1
