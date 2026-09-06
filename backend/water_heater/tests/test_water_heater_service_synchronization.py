import pytest

from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory
from water_heater.services.water_heater_synchronization import (
    queue_water_heaters_to_turn_on,
    resolve_water_heaters_to_update,
    turn_off_water_heaters_and_apply_to_hardware,
)
from water_heater.utils.cache_water_heater import get_water_heaters_to_turn_on_in_cache

PLAN_STATE_WANTS_ON = {
    "water_heater_id": 1,
    "water_heater__requested_state": WaterHeater.RequestedState.OFF,
    "water_heater__power": 2000,
    "plan_requested_state": WaterHeater.RequestedState.ON,
}
PLAN_STATE_WANTS_OFF = {
    "water_heater_id": 2,
    "water_heater__requested_state": WaterHeater.RequestedState.ON,
    "water_heater__power": 2000,
    "plan_requested_state": WaterHeater.RequestedState.OFF,
}
PLAN_STATE_ALREADY_ON = {
    "water_heater_id": 3,
    "water_heater__requested_state": WaterHeater.RequestedState.ON,
    "water_heater__power": 2000,
    "plan_requested_state": WaterHeater.RequestedState.ON,
}
PLAN_STATE_LOAD_SHED_STAYS_SHED = {
    "water_heater_id": 4,
    "water_heater__requested_state": WaterHeater.RequestedState.LOAD_SHED,
    "water_heater__power": 2000,
    "plan_requested_state": WaterHeater.RequestedState.ON,
}
PLAN_STATE_NO_OPINION = {
    "water_heater_id": 5,
    "water_heater__requested_state": WaterHeater.RequestedState.ON,
    "water_heater__power": 2000,
    "plan_requested_state": None,
}


def test_resolve_water_heaters_to_update():
    result = resolve_water_heaters_to_update(
        [
            PLAN_STATE_WANTS_ON,
            PLAN_STATE_WANTS_OFF,
            PLAN_STATE_ALREADY_ON,
            PLAN_STATE_LOAD_SHED_STAYS_SHED,
            PLAN_STATE_NO_OPINION,
        ]
    )

    assert result == {
        "to_turn_on": [{"id": 1, "power": 2000}, {"id": 4, "power": 2000}],
        "ids_to_turn_off": [2],
    }


def test_resolve_water_heaters_to_update_load_shed_is_requeued_for_retry():
    """A LOAD_SHED water heater whose plan still wants ON is put back in
    the to_turn_on queue (not forced directly to ON) — same self-healing
    retry mechanism as radiators: the listener decides, from there,
    whether there's now enough power to actually turn it back on."""
    result = resolve_water_heaters_to_update([PLAN_STATE_LOAD_SHED_STAYS_SHED])

    assert result == {"to_turn_on": [{"id": 4, "power": 2000}], "ids_to_turn_off": []}


def test_resolve_water_heaters_to_update_empty_input():
    assert resolve_water_heaters_to_update([]) == {
        "to_turn_on": [],
        "ids_to_turn_off": [],
    }


@pytest.mark.django_db
def test_turn_off_water_heaters_and_apply_to_hardware(mocker):
    mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=False)
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.ON)

    turn_off_water_heaters_and_apply_to_hardware(
        {"ids_to_turn_off": [water_heater.id], "to_turn_on": []}
    )

    water_heater.refresh_from_db()
    # requested_state written directly to DB
    assert water_heater.requested_state == WaterHeater.RequestedState.OFF
    # applied to hardware immediately (WaterHeaterSyncService ran)
    assert water_heater.actual_state == WaterHeater.ActualState.OFF


@pytest.mark.django_db
def test_queue_water_heaters_to_turn_on():
    water_heater = WaterHeaterFactory(requested_state=WaterHeater.RequestedState.OFF)

    queue_water_heaters_to_turn_on(
        {
            "to_turn_on": [{"id": water_heater.id, "power": 2000}],
            "ids_to_turn_off": [],
        }
    )

    water_heater.refresh_from_db()
    # requested_state is NOT changed here
    assert water_heater.requested_state == WaterHeater.RequestedState.OFF
    # only added to the cache, for the teleinfo listener to decide
    assert get_water_heaters_to_turn_on_in_cache() == [
        {"id": water_heater.id, "power": 2000}
    ]
