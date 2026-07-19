def wh_to_watt(wh: float, duration_minutes: float) -> float | None:
    """Convert a watt-hour value over a duration into an average watt value.

    Returns None if wh isn't a number, or if duration_minutes is falsy (0 or None)
    since that would divide by zero.
    """
    if not isinstance(wh, (int, float)):
        return None
    if not duration_minutes:
        return None
    duration_hours = duration_minutes / 60
    return wh / duration_hours
