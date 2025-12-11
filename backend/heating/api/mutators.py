from datetime import date

from django.db import transaction
from django.utils import timezone
from heating.models import RoomHeatingDayPlan


@transaction.atomic
def duplicate_heating_plan_with_override(
    room_id: int, heating_pattern_id: int, duplication_dates: list[date]
) -> int:
    now = timezone.now()
    plans_to_create = [
        RoomHeatingDayPlan(
            room_id=room_id,
            date=date,
            heating_pattern_id=heating_pattern_id,
            created_at=now,
            updated_at=now,
        )
        for date in duplication_dates
    ]

    results = RoomHeatingDayPlan.objects.bulk_create(
        plans_to_create,
        update_conflicts=True,
        update_fields=["heating_pattern", "updated_at"],
        unique_fields=["room", "date"],
    )

    return len(results)
