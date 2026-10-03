from datetime import date

from django.db import transaction
from django.utils import timezone


@transaction.atomic
def duplicate_equipment_plan_with_override(
    config, equipment_id: int, schedule_pattern_id: int, duplication_dates: list[date]
) -> int:
    """
    Overwrites the plan of `equipment_id` on each of `duplication_dates`
    with `schedule_pattern_id`, creating the missing day-plan rows.

    `config` only needs an `equipment_dayplan` attribute (duck-typed, like
    in planning.api.selectors) so this stays free of any import from a
    concrete equipment app. The upsert relies on the (equipment, date)
    unique constraint every concrete day-plan model must declare.
    """
    day_plan_model = config.equipment_dayplan
    now = timezone.now()
    plans_to_create = [
        day_plan_model(
            equipment_id=equipment_id,
            date=single_date,
            schedule_pattern_id=schedule_pattern_id,
            created_at=now,
            updated_at=now,
        )
        for single_date in duplication_dates
    ]

    results = day_plan_model.objects.bulk_create(
        plans_to_create,
        update_conflicts=True,
        update_fields=["schedule_pattern", "updated_at"],
        unique_fields=["equipment", "date"],
    )
    return len(results)
