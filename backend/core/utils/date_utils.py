from datetime import date, datetime, timedelta

from core.constants import WeekDayLabel


def is_delta_within_one_minute(dt1: datetime, dt2: datetime) -> bool:
    """Check if the difference between two datetime objects is less than or equal to 1 minute."""
    return abs(dt1 - dt2) <= timedelta(minutes=1)


def is_delta_within_two_minute(dt1: datetime, dt2: datetime) -> bool:
    """Check if the difference between two datetime objects is less than or equal to 2 minute."""
    return abs(dt1 - dt2) <= timedelta(minutes=2)


def is_delta_within_five_seconds(dt1: datetime, dt2: datetime) -> bool:
    """Check if the difference between two datetime objects is less than or equal to 2 minute."""
    return abs(dt1 - dt2) <= timedelta(seconds=5)


def parse_iso_datetime(dt_str: str) -> datetime | None:
    """Convert an ISO 8601 datetime string (e.g., "2025-10-15T10:55:53.438Z") to a datetime object."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return None


def weekdays_str_list_to_datetime_weekdays_list(labels: list[str]) -> list[int] | None:
    if not isinstance(labels, list):
        return
    mapping = {
        WeekDayLabel.MONDAY: 0,
        WeekDayLabel.TUESDAY: 1,
        WeekDayLabel.WEDNESDAY: 2,
        WeekDayLabel.THURSDAY: 3,
        WeekDayLabel.FRIDAY: 4,
        WeekDayLabel.SATURDAY: 5,
        WeekDayLabel.SUNDAY: 6,
    }

    result = []
    for label in labels:
        try:
            enum_value = WeekDayLabel(label)
        except ValueError:
            return

        result.append(mapping[enum_value])

    return result


def get_week_containing_date(day: date) -> list[date]:
    if not isinstance(day, date):
        return []
    start = day - timedelta(days=day.weekday())
    return [start + timedelta(days=i) for i in range(7)]


def get_previous_monday(day: date) -> date | None:
    try:
        return day - timedelta(days=day.weekday())
    except AttributeError:
        return


def get_next_sunday(day: date) -> date | None:
    try:
        return day - timedelta(days=day.weekday()) + timedelta(days=6)
    except AttributeError:
        return
