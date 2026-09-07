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


def split_by_available_power(
    items: list, remaining_power: int | None
) -> tuple[list, list]:
    """
    Splits a list of {"power": ..., ...} dicts into (can_turn_on,
    cannot_turn_on), greedily allocating from remaining_power in list
    order.

    If remaining_power is None (instant power unknown, e.g. teleinfo
    unavailable) or <= 0, nothing is considered safe to turn on.
    """
    if remaining_power is None or remaining_power <= 0:
        return [], items

    can_turn_on = []
    cannot_turn_on = []

    for item in items:
        if remaining_power >= item["power"]:
            can_turn_on.append(item)
            remaining_power -= item["power"]
        else:
            cannot_turn_on.append(item)

    return can_turn_on, cannot_turn_on
