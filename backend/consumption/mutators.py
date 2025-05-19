import logging
from core.constants import LoggerLabel
from consumption.utils import generate_daily_index_structure
from teleinfo.constants import TELEINFO_INDEX_LABELS
from consumption.models import DailyConsumption
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger("django")


def save_teleinfo_data():
    now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
    now_date = now.date()
    minute_str = now.strftime("%H:%M")

    cache_teleinfo_data = cache.get("teleinfo_data", {})
    cache_last_read = cache_teleinfo_data.get("last_read")
    if cache_last_read:
        cache_last_read = timezone.localtime(cache_last_read).replace(
            second=0, microsecond=0
        )

    if cache_last_read != now:
        logger.warning(
            f"{LoggerLabel.CONSUMPTION} The cache is not up to date, we do not save"
        )
        return

    indexes_in_teleinfo = {
        key: value
        for key, value in cache_teleinfo_data.items()
        if key in TELEINFO_INDEX_LABELS
    }

    # Update current day

    daily_consumption, _ = DailyConsumption.objects.get_or_create(
        date=now_date,
        defaults={
            "values": generate_daily_index_structure(),
        },
    )
    daily_consumption.values[minute_str] = indexes_in_teleinfo
    daily_consumption.save()

    # If it's midnight, update "24:00" of the previous day
    if minute_str == "00:00":
        previous_day = now_date - timezone.timedelta(days=1)

        previous_consumption, _ = DailyConsumption.objects.get_or_create(
            date=previous_day,
            defaults={
                "values": generate_daily_index_structure(),
            },
        )
        previous_consumption.values["24:00"] = indexes_in_teleinfo
        previous_consumption.save()
