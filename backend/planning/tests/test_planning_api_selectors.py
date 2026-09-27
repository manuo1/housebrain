from datetime import date

import pytest

from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory
from planning.api.selectors import get_equipment_day_plans
from planning.api.views import SchedulableEquipment
from planning.tests.factories import SchedulePatternFactory
from water_heater.models import WaterHeaterDayPlan
from water_heater.tests.factories import WaterHeaterDayPlanFactory

WATER_HEATER_CONFIG = SchedulableEquipment(
    type_name="water_heater",
    equipment_dayplan=WaterHeaterDayPlan,
    equipment_model=WaterHeater,
)

DEFAULT_DATE = date(2025, 12, 10)


@pytest.mark.django_db
def test_invalid_date_returns_empty_list():
    assert get_equipment_day_plans([WATER_HEATER_CONFIG], "not-a-date") == []


@pytest.mark.django_db
def test_equipment_with_no_plan_has_empty_slots():
    water_heater = WaterHeaterFactory(name="Cumulus")

    result = get_equipment_day_plans([WATER_HEATER_CONFIG], DEFAULT_DATE)

    assert result == [
        {
            "type": "water_heater",
            "id": water_heater.id,
            "name": "Cumulus",
            "slots": [],
        }
    ]


@pytest.mark.django_db
def test_equipment_with_plan_returns_its_slots():
    slots = [{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    water_heater = WaterHeaterFactory(name="Cumulus")
    WaterHeaterDayPlanFactory(
        equipment=water_heater,
        date=DEFAULT_DATE,
        schedule_pattern=SchedulePatternFactory(slots=slots),
    )

    result = get_equipment_day_plans([WATER_HEATER_CONFIG], DEFAULT_DATE)

    assert result == [
        {
            "type": "water_heater",
            "id": water_heater.id,
            "name": "Cumulus",
            "slots": slots,
        }
    ]


@pytest.mark.django_db
def test_only_returns_plans_for_the_requested_date():
    slots = [{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    water_heater = WaterHeaterFactory()
    WaterHeaterDayPlanFactory(
        equipment=water_heater,
        date=date(2025, 12, 11),  # different day
        schedule_pattern=SchedulePatternFactory(slots=slots),
    )

    result = get_equipment_day_plans([WATER_HEATER_CONFIG], DEFAULT_DATE)

    assert result[0]["slots"] == []


@pytest.mark.django_db
def test_multiple_equipment_types_are_all_included():
    """One query pair per registered type: exercising the loop with two
    entries in schedulable_equipments (reusing the same models under a
    different type_name — no second equipment app exists yet to test
    with) confirms both are aggregated, not just the first."""
    water_heater = WaterHeaterFactory(name="Cumulus")
    other_type_config = SchedulableEquipment(
        type_name="other_type",
        equipment_dayplan=WaterHeaterDayPlan,
        equipment_model=WaterHeater,
    )

    result = get_equipment_day_plans(
        [WATER_HEATER_CONFIG, other_type_config], DEFAULT_DATE
    )

    types_returned = {row["type"] for row in result}
    assert types_returned == {"water_heater", "other_type"}
    assert len(result) == 2
    assert all(row["id"] == water_heater.id for row in result)


@pytest.mark.django_db
def test_no_registered_equipment_types_returns_empty_list():
    WaterHeaterFactory()
    assert get_equipment_day_plans([], DEFAULT_DATE) == []
