from collections import defaultdict
from datetime import date, timedelta

from heating.api.constants import DayStatus, DuplicationTypes
from heating.api.selectors import get_slots_hashes


def group_slots_hashes_by_date(slots_hashes: list) -> None:
    day_to_hashes = defaultdict(set)
    try:
        for d, h in slots_hashes:
            day_to_hashes[d].add(h)
    except TypeError:
        return {}
    return day_to_hashes


def add_day_status(raw_calendar: list) -> list:
    if not isinstance(raw_calendar, list):
        return []
    try:
        calendar_start_date = raw_calendar[0]["date"]
        calendar_end_date = raw_calendar[-1]["date"]
        qs_start_date = calendar_start_date - timedelta(weeks=1)
    except (IndexError, KeyError, TypeError):
        return []

    slots_hashes = get_slots_hashes(qs_start_date, calendar_end_date)
    if not slots_hashes:
        return raw_calendar
    dates_slots_hashes = group_slots_hashes_by_date(slots_hashes)
    for day in raw_calendar:
        day_date = day.get("date")
        if day_date is None:
            continue
        day_hashes = dates_slots_hashes.get(day_date)

        # day without a heating plan
        if day_hashes is None:
            day["status"] = DayStatus.EMPTY
            continue

        # day having the same heating plans as the same day of the previous week
        day_of_previous_week = day_date - timedelta(weeks=1)
        day_of_previous_week_hashes = dates_slots_hashes.get(day_of_previous_week)
        if day_hashes == day_of_previous_week_hashes:
            day["status"] = DayStatus.NORMAL
            continue

        # day not having the same heating plans as the same day of the previous week
        else:
            day["status"] = DayStatus.DIFFERENT

    return raw_calendar


def error_in_duplication_dates(source_date, start_date, end_date, duplication_type):
    # start_date must be strictly after source_date
    if start_date <= source_date:
        return "start_date must be strictly after source_date"

    # end_date must be strictly after start_date
    if end_date <= start_date:
        return "end_date must be strictly after start_date"

    # For WEEK duplications, there must be at least 6 days between the start_date and end_date.
    if duplication_type == DuplicationTypes.WEEK:
        days_diff = (end_date - start_date).days
        if days_diff < 6:
            return (
                "end_date must be at least 6 days after start_date for week duplication"
            )

    # Maximum 365 days between start_date and end_date
    days_diff = (end_date - start_date).days
    if days_diff > 365:
        return "Maximum 365 days allowed between start_date and end_date"

    return None


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
