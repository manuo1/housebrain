from datetime import date

from heating.models import RoomHeatingDayPlan


def get_slots_hashes(start_date: date, end_date: date) -> list:
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        return []
    return list(
        RoomHeatingDayPlan.objects.filter(
            date__gte=start_date, date__lte=end_date
        ).values_list("date", "heating_pattern__slots_hash")
    )
