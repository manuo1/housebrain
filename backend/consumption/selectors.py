from consumption.models import DailyIndexes
from datetime import date


def get_daily_indexes(start: date, end: date) -> list[DailyIndexes]:
    return list(
        DailyIndexes.objects.filter(date__gte=start, date__lt=end).order_by("date")
    )
