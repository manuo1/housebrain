from actuators.models import Radiator
from rooms.api.constants import ApiRadiatorState, TemperatureTrend


def get_mac_short(mac_address: str | None) -> str | None:
    """
    Return the last 3 segments of a MAC address if possible.
    Works even if the input string is shorter than expected.
    """
    if isinstance(mac_address, str):
        return mac_address[-8:]
    return None


def calculate_temperature_trend(
    current_temp: float | None, previous_temp: float | None, threshold=0.1
) -> str | None:
    """
    Calculate the temperature trend between two measurements.
    """
    try:
        diff = current_temp - previous_temp

        if diff > threshold:
            return TemperatureTrend.UP
        elif diff < -threshold:
            return TemperatureTrend.DOWN
        else:
            return TemperatureTrend.SAME
    except (TypeError, ValueError):
        return None


def calculate_radiator_state(
    requested_state: Radiator.RequestedState | None,
    actual_state: Radiator.ActualState | None,
) -> str | None:
    """
    Calculate the radiator state based on requested and actual states.
    """

    if not requested_state or not actual_state:
        return None

    if actual_state == Radiator.ActualState.UNDEFINED:
        return ApiRadiatorState.UNDEFINED

    state_map: dict[tuple[str, str], str] = {
        (Radiator.RequestedState.ON, Radiator.ActualState.ON): ApiRadiatorState.ON,
        (
            Radiator.RequestedState.ON,
            Radiator.ActualState.OFF,
        ): ApiRadiatorState.TURNING_ON,
        (Radiator.RequestedState.OFF, Radiator.ActualState.OFF): ApiRadiatorState.OFF,
        (
            Radiator.RequestedState.OFF,
            Radiator.ActualState.ON,
        ): ApiRadiatorState.SHUTTING_DOWN,
        (
            Radiator.RequestedState.LOAD_SHED,
            Radiator.ActualState.ON,
        ): ApiRadiatorState.SHUTTING_DOWN,
        (
            Radiator.RequestedState.LOAD_SHED,
            Radiator.ActualState.OFF,
        ): ApiRadiatorState.LOAD_SHED,
    }

    return state_map.get((requested_state, actual_state))
