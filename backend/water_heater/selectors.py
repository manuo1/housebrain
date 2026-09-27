from datetime import date

from django.utils import timezone

from equipment.models import WaterHeater
from planning.models import SchedulePattern
from planning.services import get_slot_data
from water_heater.mappers import (
    schedule_pattern_slot_value_to_water_heater_requested_state,
)
from water_heater.models import WaterHeaterDayPlan


def get_water_heaters_plans_data(day: date) -> list[dict]:
    # Query on the renamed generic FK (`equipment`), but republish with
    # water_heater_* keys — downstream (get_water_heaters_plan_states,
    # water_heater_synchronization.py, and their tests) is business logic
    # specific to water heaters and reads more clearly that way.
    rows = WaterHeaterDayPlan.objects.filter(date=day).values(
        "equipment_id",
        "schedule_pattern__slots",
        "equipment__requested_state",
        "equipment__power",
        "equipment__importance",
    )
    return [
        {
            "water_heater_id": row["equipment_id"],
            "schedule_pattern__slots": row["schedule_pattern__slots"],
            "water_heater__requested_state": row["equipment__requested_state"],
            "water_heater__power": row["equipment__power"],
            "water_heater__importance": row["equipment__importance"],
        }
        for row in rows
    ]


def get_water_heaters_plan_states() -> list[dict]:
    """
    Resolves today's plan for each water heater into the state the plan
    currently wants (ON/OFF/None) — the only function in this module that
    depends on the current time. Kept separate from
    resolve_water_heaters_to_update so that one stays pure/time-free and
    easy to unit test.
    """
    now = timezone.localtime(timezone.now())

    water_heaters_plan_states = []
    for plan in get_water_heaters_plans_data(now.date()):
        slot_type, slot_value = get_slot_data(
            plan["schedule_pattern__slots"], now.time()
        )

        plan_requested_state = WaterHeater.RequestedState.OFF
        if slot_type == SchedulePattern.SlotType.ONOFF:
            plan_requested_state = (
                schedule_pattern_slot_value_to_water_heater_requested_state(slot_value)
            )

        water_heaters_plan_states.append(
            {
                "water_heater_id": plan["water_heater_id"],
                "water_heater__requested_state": plan["water_heater__requested_state"],
                "water_heater__power": plan["water_heater__power"],
                "water_heater__importance": plan["water_heater__importance"],
                "plan_requested_state": plan_requested_state,
            }
        )

    return water_heaters_plan_states


def get_water_heaters_data_for_load_shedding() -> list[dict]:
    """
    Return the minimum info needed for load shedding, sorted from lowest
    to highest priority (mirrors
    actuators.selectors.radiators.get_radiators_data_for_load_shedding).
    """
    return list(
        WaterHeater.objects.filter(actual_state=WaterHeater.ActualState.ON, power__gt=0)
        .order_by("-importance", "-power")
        .values("id", "power", "importance")
    )
