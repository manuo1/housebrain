from datetime import date, time, timedelta

# Shared by the AI duplication flow of every schedulable equipment (heating
# included), so they live here rather than in any one equipment's app.
AI_DUPLICATION_MAX_DAYS = 365
AI_DUPLICATION_WARNING_THRESHOLD = 30

FRENCH_WEEKDAYS = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

FRENCH_MONTHS = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]


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


def generate_duplication_dates(
    start_date: date, weekdays: list[int], end_date: date
) -> list[date]:
    weekdays = sorted(set(weekdays))
    dates = []

    for weekday in weekdays:
        # Calculate the number of days until the next requested weekday
        days_ahead = (weekday - start_date.weekday()) % 7

        # If it's 0, it means start_date is already on this weekday
        if days_ahead == 0:
            next_date = start_date
        else:
            next_date = start_date + timedelta(days=days_ahead)

        # Add all occurrences of this day until end_date
        while next_date <= end_date:
            dates.append(next_date)
            next_date += timedelta(days=7)

    dates.sort()
    return dates


def format_date_fr(day: date) -> str:
    """Formats a date as "lundi 18 août 2026" (French, spelled out weekday and month)."""
    return f"{FRENCH_WEEKDAYS[day.weekday()]} {day.day} {FRENCH_MONTHS[day.month - 1]} {day.year}"


def join_fr(items: list[str]) -> str:
    """Joins items with commas and "et" before the last one, from 2 items up ("a et b", "a, b et c")."""
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " et " + items[-1]
