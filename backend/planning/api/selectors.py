from datetime import date

from planning.models import SchedulePattern


def get_schedulable_equipment_config(schedulable_equipments: list, type_name: str):
    for config in schedulable_equipments:
        if config.type_name == type_name:
            return config
    return None


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


def invalid_equipment_refs_in_plans(
    schedulable_equipments: list, plans: list[dict]
) -> list[dict]:
    """
    Returns the {type, id} pairs from `plans` that don't match a
    registered type_name, or whose id doesn't exist for that type's
    equipment_model. One query per distinct type in `plans`, not one per
    plan entry.
    """
    ids_by_type: dict[str, set[int]] = {}
    for plan in plans:
        ids_by_type.setdefault(plan["type"], set()).add(plan["id"])

    invalid = []
    for type_name, ids in ids_by_type.items():
        config = get_schedulable_equipment_config(schedulable_equipments, type_name)
        if config is None:
            invalid.extend({"type": type_name, "id": i} for i in ids)
            continue

        existing_ids = set(
            config.equipment_model.objects.filter(id__in=ids).values_list(
                "id", flat=True
            )
        )
        invalid.extend({"type": type_name, "id": i} for i in ids - existing_ids)

    return invalid


def get_equipment_names_by_type_and_ids(
    schedulable_equipments: list, refs: set[tuple[str, int]]
) -> dict[tuple[str, int], str]:
    ids_by_type: dict[str, set[int]] = {}
    for type_name, equipment_id in refs:
        ids_by_type.setdefault(type_name, set()).add(equipment_id)

    names = {}
    for type_name, ids in ids_by_type.items():
        config = get_schedulable_equipment_config(schedulable_equipments, type_name)
        if config is None:
            continue
        for equipment_id, name in config.equipment_model.objects.filter(
            id__in=ids
        ).values_list("id", "name"):
            names[(type_name, equipment_id)] = name

    return names


def get_equipment_day_plan_data(
    schedulable_equipments: list, day: date, refs: set[tuple[str, int]]
) -> list[tuple[str, int, int]]:
    """
    Returns (type_name, equipment_id, schedule_pattern_id) for each ref in
    `refs` (a set of (type_name, equipment_id)), read from `day`'s plans.

    An equipment without a plan on `day` is returned with the empty
    pattern rather than skipped, so duplicating an empty day also empties
    the target days (same behavior as the heating duplication). Refs whose
    type_name isn't registered are skipped: callers are expected to have
    validated them beforehand.

    One query per equipment type, regardless of how many instances.
    """
    if not isinstance(day, date) or not isinstance(refs, set) or not refs:
        return []

    ids_by_type: dict[str, set[int]] = {}
    for type_name, equipment_id in refs:
        ids_by_type.setdefault(type_name, set()).add(equipment_id)

    results = []
    empty_pattern_id = None
    for type_name, ids in ids_by_type.items():
        config = get_schedulable_equipment_config(schedulable_equipments, type_name)
        if config is None:
            continue

        existing = list(
            config.equipment_dayplan.objects.filter(
                date=day, equipment_id__in=ids
            ).values_list("equipment_id", "schedule_pattern_id")
        )
        results.extend((type_name, eid, pid) for eid, pid in existing)

        missing_ids = ids - {eid for eid, _ in existing}
        if missing_ids:
            if empty_pattern_id is None:
                empty_pattern_id = SchedulePattern.get_or_create_from_slots([])[0].id
            results.extend((type_name, eid, empty_pattern_id) for eid in missing_ids)

    return results
