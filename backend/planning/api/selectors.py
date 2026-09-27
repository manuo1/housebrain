from datetime import date


def get_equipment_day_plans(schedulable_equipments: list, day: date) -> list[dict]:
    """
    For each registered schedulable equipment type, list every equipment
    instance with its slots for `day` (empty list if no day-plan row
    exists yet for that equipment/date).

    `schedulable_equipments` items only need `type_name`,
    `equipment_dayplan` and `equipment_model` attributes (duck-typed) —
    this stays free of any import from a concrete equipment app.

    One query per equipment type for day-plans + one for the equipment
    list, regardless of how many instances exist (no N+1 per instance).
    """
    if not isinstance(day, date):
        return []

    results = []
    for config in schedulable_equipments:
        slots_by_equipment_id = dict(
            config.equipment_dayplan.objects.filter(date=day).values_list(
                "equipment_id", "schedule_pattern__slots"
            )
        )
        for equipment in config.equipment_model.objects.all().values("id", "name"):
            results.append(
                {
                    "type": config.type_name,
                    "id": equipment["id"],
                    "name": equipment["name"],
                    "slots": slots_by_equipment_id.get(equipment["id"], []),
                }
            )

    return results
