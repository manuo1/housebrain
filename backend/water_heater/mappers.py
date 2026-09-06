from equipment.models import WaterHeater


def water_heater_state_matches_plan_state(
    plan_requested_state: WaterHeater.RequestedState | None,
    water_heater_requested_state: WaterHeater.RequestedState,
) -> bool:
    match plan_requested_state:
        case WaterHeater.RequestedState.ON:
            return water_heater_requested_state == WaterHeater.RequestedState.ON
        case WaterHeater.RequestedState.OFF:
            return water_heater_requested_state in (
                WaterHeater.RequestedState.OFF,
                WaterHeater.RequestedState.LOAD_SHED,
            )
        case None:
            return water_heater_requested_state is None
        case _:
            return False


def schedule_pattern_slot_value_to_water_heater_requested_state(
    slot_value: str,
) -> WaterHeater.RequestedState | None:
    """
    Unlike heating_pattern_slot_value_to_room_requested_heating_state,
    returns None (not an UNKNOWN choice) for an unrecognized value —
    WaterHeater.RequestedState has no UNKNOWN member, None here means
    "the plan has no opinion right now".
    """
    if not isinstance(slot_value, str):
        return None
    mapping = {
        "on": WaterHeater.RequestedState.ON,
        "off": WaterHeater.RequestedState.OFF,
    }
    return mapping.get(slot_value)
