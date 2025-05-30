import logging
from core.constants import LoggerLabel
from consumption.utils import generate_daily_index_structure
from teleinfo.constants import TELEINFO_INDEX_LABELS
from consumption.models import DailyIndexes
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger("django")


def save_teleinfo_data():
    now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
    now_date = now.date()
    now_minute_str = now.strftime("%H:%M")

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
        key: int(value)
        for key, value in cache_teleinfo_data.items()
        if key in TELEINFO_INDEX_LABELS
    }

    # Update current day

    daily_indexes, _ = DailyIndexes.objects.get_or_create(
        date=now_date, defaults={"values": {}}
    )

    for label, value in indexes_in_teleinfo.items():
        try:
            daily_indexes.values[label][now_minute_str] = value
        except KeyError:
            daily_indexes.values[label] = generate_daily_index_structure()
            daily_indexes.values[label][now_minute_str] = value
    daily_indexes.save()

    # If it's midnight, update "24:00" of the previous day
    if now_minute_str == "00:00":
        previous_day = now_date - timezone.timedelta(days=1)

        previous_day_indexes, _ = DailyIndexes.objects.get_or_create(
            date=previous_day, defaults={}
        )

        for label, value in indexes_in_teleinfo.items():
            try:
                previous_day_indexes.values[label]["24:00"] = value
            except KeyError:
                previous_day_indexes.values[label] = generate_daily_index_structure()
                previous_day_indexes.values[label]["24:00"] = value
        previous_day_indexes.save()
