from datetime import date

from django.db.models import F, JSONField, OuterRef, Subquery, Value

# from django.db.models.fields.json import JSONField
from django.db.models.functions import Coalesce
from heating.models import RoomHeatingDayPlan
from rooms.models import Room


def get_slots_hashes(start_date: date, end_date: date) -> list:
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        return []
    return list(
        RoomHeatingDayPlan.objects.filter(
            date__gte=start_date, date__lte=end_date
        ).values_list("date", "heating_pattern__slots_hash")
    )


def get_daily_heating_plan(day: date) -> list:
    if not isinstance(day, date):
        return []

    slots_subquery = RoomHeatingDayPlan.objects.filter(
        room_id=OuterRef("id"), date=day
    ).values("heating_pattern__slots")[:1]

    qs = (
        Room.objects.filter(radiator__isnull=False)
        .annotate(
            room_id=F("id"),
            slots=Coalesce(
                Subquery(slots_subquery, output_field=JSONField()),
                Value([], output_field=JSONField()),
            ),
        )
        .order_by("name", "room_id")
        .values("room_id", "name", "slots")
    )

    return list(qs)


def invalid_room_ids(room_ids: list) -> set:
    room_ids_in_db = set(
        Room.objects.filter(id__in=room_ids).values_list("id", flat=True)
    )
    return set(room_ids) - room_ids_in_db


def invalid_room_ids_in_plans(plans: list) -> set:
    room_ids_in_request = [plan["room_id"] for plan in plans]

    return invalid_room_ids(room_ids_in_request)


def get_room_heating_day_plan_data(day: date, room_id: list[int]) -> list[dict]:
    return list(
        RoomHeatingDayPlan.objects.filter(date=day, room_id__in=room_id).values_list(
            "room_id", "heating_pattern_id"
        )
    )
