from enum import StrEnum


def validate_temperature_value(temperature_value: object) -> float | None:
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
