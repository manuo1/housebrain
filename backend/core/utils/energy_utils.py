def wh_to_watt(wh: float, duration_minutes: float) -> float:
    """Convert watt hour to watt"""
    if not isinstance(wh, (int, float)):
        return None
    if not duration_minutes:
        return None
    duration_hours = duration_minutes / 60
    return wh / duration_hours
