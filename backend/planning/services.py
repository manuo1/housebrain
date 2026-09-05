from datetime import time


def get_slot_data(slots: list, searched_time: time) -> tuple:
    """
    Find the slot in `slots` (a SchedulePattern.slots list) that contains
    `searched_time`, and return its (type, value). Returns (None, None)
    if no slot matches or the input is malformed.

    Generic over slot type (temp/onoff/whatever gets added later, e.g. a
    water heater temperature sensor) — callers decide what to do with
    the returned type/value pair.
    """
    if not isinstance(slots, list) or not isinstance(searched_time, time):
        return None, None

    for slot in slots:
        try:
            start_h, start_m = map(int, slot["start"].split(":"))
            end_h, end_m = map(int, slot["end"].split(":"))
            start_t = time(start_h, start_m)
            end_t = time(end_h, end_m)
        except (ValueError, KeyError, TypeError):
            continue

        if start_t <= searched_time <= end_t:
            try:
                return slot["type"], slot["value"]
            except (ValueError, KeyError):
                continue

    return None, None
