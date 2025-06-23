import logging
from consumption.utils import (
    add_new_tarif_period,
    add_new_values,
    get_cache_teleinfo_data,
    get_indexes_in_teleinfo,
    get_subscribed_power,
    get_tarif_period,
)
from consumption.models import DailyIndexes
from django.utils import timezone


logger = logging.getLogger("django")


def save_teleinfo_data():
    now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
    now_date = now.date()
    now_minute_str = now.strftime("%H:%M")

    cache_teleinfo_data = get_cache_teleinfo_data(now)

    if cache_teleinfo_data is None:
        return

    indexes_in_teleinfo = get_indexes_in_teleinfo(cache_teleinfo_data)
    tarif_period = get_tarif_period(cache_teleinfo_data)
    subscribed_power = get_subscribed_power(cache_teleinfo_data)

    # Update current day
    bdd_today_indexes, _ = DailyIndexes.objects.get_or_create(
        date=now_date,
        defaults={
            "values": {},
            "tarif_periods": {},
            "subscribed_power": None,
        },
    )

    bdd_today_indexes.subscribed_power = subscribed_power
    bdd_today_indexes.tarif_periods = add_new_tarif_period(
        bdd_today_indexes.tarif_periods, now_minute_str, tarif_period
    )

    bdd_today_indexes = add_new_values(
        bdd_today_indexes, indexes_in_teleinfo, now_minute_str
    )

    bdd_today_indexes.save()

    # If it's midnight, update "24:00" of the previous day
    if now_minute_str == "00:00":
        previous_day = now_date - timezone.timedelta(days=1)

        bdd_previous_day_indexes, _ = DailyIndexes.objects.get_or_create(
            date=previous_day,
            defaults={
                "values": {},
                "tarif_periods": {},
                "subscribed_power": None,
            },
        )

        bdd_previous_day_indexes.subscribed_power = subscribed_power
        bdd_previous_day_indexes.tarif_periods = add_new_tarif_period(
            bdd_previous_day_indexes.tarif_periods, "24:00", tarif_period
        )

        bdd_previous_day_indexes = add_new_values(
            bdd_previous_day_indexes, indexes_in_teleinfo, "24:00"
        )

        bdd_previous_day_indexes.save()
