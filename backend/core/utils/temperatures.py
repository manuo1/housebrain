def validate_temperature_value(temperature_value: object) -> float | None:
    if isinstance(temperature_value, bool):
        return
    try:
        return float(temperature_value)
    except (ValueError, TypeError):
        return
