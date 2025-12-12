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


def error_in_duplication_dates(source_date, end_date, duplication_type):
    if source_date >= end_date:
        return "source_date must be before repeat_until"
    if (end_date - source_date).days > 366:
        return "Maximum 365 days between source_date and repeat_until"
    if duplication_type == DuplicationTypes.WEEK and (end_date - source_date).days < 7:
        return "There must be at least 7 days between source_date and repeat_until in the case of a duplication of weeks"


def generate_duplication_dates(
    source_date: date, weekdays: list[int], end_date: date
) -> list[date]:
    weekdays = sorted(set(weekdays))
    dates = []
    current_date = source_date + timedelta(days=1)

    for weekday in sorted(weekdays):
        days_ahead = (weekday - current_date.weekday()) % 7
        if days_ahead == 0 and current_date <= source_date:
            days_ahead = 7
        next_date = current_date + timedelta(days=days_ahead)

        while next_date <= end_date:
            dates.append(next_date)
            next_date += timedelta(days=7)

    dates.sort()
    return dates
