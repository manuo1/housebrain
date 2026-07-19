from enum import StrEnum


def validate_temperature_value(temperature_value: object) -> float | None:
    """Coerce a raw value to a float temperature, rejecting booleans and anything non-numeric.

    Returns None if the value can't be converted (or is a bool, which isinstance(float)
    checks would otherwise let through since bool is a subclass of int).
    """
    if isinstance(temperature_value, bool):
        return
    try:
        return float(temperature_value)
    except (ValueError, TypeError):
        return


class TemperatureTrend(StrEnum):
    UP = "up"
    DOWN = "down"
    SAME = "same"


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
