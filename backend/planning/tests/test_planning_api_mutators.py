from datetime import date

import pytest

from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory
from planning.api.mutators import duplicate_equipment_plan_with_override
from planning.api.views import SchedulableEquipment
from planning.tests.factories import SchedulePatternFactory, SchedulePatternOnOffFactory
from water_heater.models import WaterHeaterDayPlan
from water_heater.tests.factories import WaterHeaterDayPlanFactory

WATER_HEATER_CONFIG = SchedulableEquipment(
    type_name="water_heater",
    equipment_dayplan=WaterHeaterDayPlan,
    equipment_model=WaterHeater,
)

DATES = [date(2025, 12, 10), date(2025, 12, 17), date(2025, 12, 24)]


@pytest.mark.django_db
def test_duplicate_creates_a_plan_on_each_date():
    water_heater = WaterHeaterFactory()
    pattern = SchedulePatternOnOffFactory()

    count = duplicate_equipment_plan_with_override(
        WATER_HEATER_CONFIG, water_heater.id, pattern.id, DATES
    )

    assert count == len(DATES)
    plans = WaterHeaterDayPlan.objects.filter(equipment=water_heater)
    assert sorted(plans.values_list("date", flat=True)) == DATES
    assert {plan.schedule_pattern_id for plan in plans} == {pattern.id}


@pytest.mark.django_db
def test_duplicate_overrides_existing_plans_without_creating_duplicates():
    water_heater = WaterHeaterFactory()
    old_pattern = SchedulePatternOnOffFactory()
    new_pattern = SchedulePatternFactory(
        slots=[{"start": "10:00", "end": "11:00", "type": "onoff", "value": "on"}]
    )
    WaterHeaterDayPlanFactory(
        equipment=water_heater, date=DATES[0], schedule_pattern=old_pattern
    )

    duplicate_equipment_plan_with_override(
        WATER_HEATER_CONFIG, water_heater.id, new_pattern.id, DATES
    )

    plans = WaterHeaterDayPlan.objects.filter(equipment=water_heater)
    assert plans.count() == len(DATES)
    assert plans.get(date=DATES[0]).schedule_pattern_id == new_pattern.id


@pytest.mark.django_db
def test_duplicate_does_not_touch_other_equipments_or_other_dates():
    target = WaterHeaterFactory(name="Cumulus")
    other = WaterHeaterFactory(name="Ballon")
    other_pattern = SchedulePatternOnOffFactory()
    new_pattern = SchedulePatternFactory(
        slots=[{"start": "10:00", "end": "11:00", "type": "onoff", "value": "on"}]
    )
    other_plan = WaterHeaterDayPlanFactory(
        equipment=other, date=DATES[0], schedule_pattern=other_pattern
    )
    untouched_date_plan = WaterHeaterDayPlanFactory(
        equipment=target, date=date(2025, 12, 11), schedule_pattern=other_pattern
    )

    duplicate_equipment_plan_with_override(
        WATER_HEATER_CONFIG, target.id, new_pattern.id, DATES
    )

    other_plan.refresh_from_db()
    untouched_date_plan.refresh_from_db()
    assert other_plan.schedule_pattern_id == other_pattern.id
    assert untouched_date_plan.schedule_pattern_id == other_pattern.id


@pytest.mark.django_db
def test_duplicate_with_no_dates_does_nothing():
    water_heater = WaterHeaterFactory()
    pattern = SchedulePatternOnOffFactory()

    count = duplicate_equipment_plan_with_override(
        WATER_HEATER_CONFIG, water_heater.id, pattern.id, []
    )

    assert count == 0
    assert WaterHeaterDayPlan.objects.count() == 0
