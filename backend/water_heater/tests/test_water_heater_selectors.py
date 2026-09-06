from datetime import date

import pytest
from freezegun import freeze_time

from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory
from planning.tests.factories import SchedulePatternFactory, SchedulePatternOnOffFactory
from water_heater.selectors import get_water_heaters_plan_states
from water_heater.tests.factories import WaterHeaterDayPlanFactory


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_plan_wants_on_during_on_slot():
    pattern = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    result = get_water_heaters_plan_states()

    assert result == [
        {
            "water_heater_id": water_heater.id,
            "water_heater__requested_state": WaterHeater.RequestedState.OFF,
            "water_heater__power": water_heater.power,
            "plan_requested_state": WaterHeater.RequestedState.ON,
        }
    ]


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_plan_wants_off_during_off_slot():
    pattern = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "off"}]
    )
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.ON)
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    result = get_water_heaters_plan_states()

    assert result[0]["plan_requested_state"] == WaterHeater.RequestedState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 10:00:00+01:00")
def test_plan_has_no_opinion_outside_slots():
    pattern = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    water_heater = WaterHeaterFactory()
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    result = get_water_heaters_plan_states()

    assert result[0]["plan_requested_state"] is None


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_plan_has_no_opinion_on_non_onoff_slot_type():
    """A temp-type slot (e.g. a future temperature-sensing water heater)
    is not handled yet."""
    pattern = SchedulePatternFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "temp", "value": 55.0}]
    )
    water_heater = WaterHeaterFactory()
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    result = get_water_heaters_plan_states()

    assert result[0]["plan_requested_state"] is None


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_no_plan_for_date_returns_empty_list():
    WaterHeaterFactory()
    # No WaterHeaterDayPlan created for today

    result = get_water_heaters_plan_states()

    assert result == []


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_multiple_water_heaters():
    pattern_on = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    pattern_off = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "off"}]
    )
    water_heater_1 = WaterHeaterFactory()
    water_heater_2 = WaterHeaterFactory()
    WaterHeaterDayPlanFactory(
        water_heater=water_heater_1,
        date=date(2025, 1, 15),
        schedule_pattern=pattern_on,
    )
    WaterHeaterDayPlanFactory(
        water_heater=water_heater_2,
        date=date(2025, 1, 15),
        schedule_pattern=pattern_off,
    )

    result = get_water_heaters_plan_states()

    result_by_id = {r["water_heater_id"]: r["plan_requested_state"] for r in result}
    assert result_by_id[water_heater_1.id] == WaterHeater.RequestedState.ON
    assert result_by_id[water_heater_2.id] == WaterHeater.RequestedState.OFF
