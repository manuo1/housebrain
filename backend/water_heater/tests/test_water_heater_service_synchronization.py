from datetime import date

import pytest
from freezegun import freeze_time

from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory
from planning.tests.factories import SchedulePatternFactory, SchedulePatternOnOffFactory
from water_heater.services.water_heater_synchronization import (
    synchronize_water_heater_requested_states_with_day_plan,
)
from water_heater.tests.factories import WaterHeaterDayPlanFactory


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_sync_during_on_slot():
    pattern = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    synchronize_water_heater_requested_states_with_day_plan()

    water_heater.refresh_from_db()
    assert water_heater.requested_state == WaterHeater.RequestedState.ON


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_sync_during_off_slot():
    pattern = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "off"}]
    )
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.ON)
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    synchronize_water_heater_requested_states_with_day_plan()

    water_heater.refresh_from_db()
    assert water_heater.requested_state == WaterHeater.RequestedState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 10:00:00+01:00")
def test_sync_outside_slots_leaves_state_unchanged():
    pattern = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    synchronize_water_heater_requested_states_with_day_plan()

    water_heater.refresh_from_db()
    assert water_heater.requested_state == WaterHeater.RequestedState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_sync_ignores_non_onoff_slot_type():
    """A temp-type slot (e.g. a future temperature-sensing water heater)
    is not handled yet -> left untouched, no crash."""
    pattern = SchedulePatternFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "temp", "value": 55.0}]
    )
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )

    synchronize_water_heater_requested_states_with_day_plan()

    water_heater.refresh_from_db()
    assert water_heater.requested_state == WaterHeater.RequestedState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_sync_no_plan_for_date_leaves_state_unchanged():
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)
    # No WaterHeaterDayPlan created for today

    synchronize_water_heater_requested_states_with_day_plan()

    water_heater.refresh_from_db()
    assert water_heater.requested_state == WaterHeater.RequestedState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_sync_multiple_water_heaters():
    pattern_on = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    pattern_off = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "off"}]
    )

    water_heater_1 = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)
    water_heater_2 = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)

    WaterHeaterDayPlanFactory(
        water_heater=water_heater_1, date=date(2025, 1, 15), schedule_pattern=pattern_on
    )
    WaterHeaterDayPlanFactory(
        water_heater=water_heater_2,
        date=date(2025, 1, 15),
        schedule_pattern=pattern_off,
    )

    synchronize_water_heater_requested_states_with_day_plan()

    water_heater_1.refresh_from_db()
    water_heater_2.refresh_from_db()

    assert water_heater_1.requested_state == WaterHeater.RequestedState.ON
    assert water_heater_2.requested_state == WaterHeater.RequestedState.OFF


@pytest.mark.django_db
@freeze_time("2025-01-15 08:00:00+01:00")
def test_sync_does_not_write_when_state_already_matches(mocker):
    pattern = SchedulePatternOnOffFactory(
        slots=[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"}]
    )
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.ON)
    WaterHeaterDayPlanFactory(
        water_heater=water_heater, date=date(2025, 1, 15), schedule_pattern=pattern
    )
    mock_update = mocker.patch(
        "water_heater.services.water_heater_synchronization.update_water_heater_requested_state"
    )

    synchronize_water_heater_requested_states_with_day_plan()

    mock_update.assert_not_called()
