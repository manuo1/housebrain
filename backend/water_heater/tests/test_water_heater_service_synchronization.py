import pytest

from core.choices import LoadSheddingImportance
from equipment.models import WaterHeater
from equipment.tests.factories import WaterHeaterFactory
from water_heater.services.water_heater_synchronization import (
    queue_water_heaters_to_turn_on,
    resolve_water_heaters_to_update,
    turn_off_water_heaters_and_apply_to_hardware,
    turn_on_water_heaters_according_to_the_available_power,
)
from water_heater.utils.cache_water_heater import get_water_heaters_to_turn_on_in_cache

PLAN_STATE_WANTS_ON = {
    "water_heater_id": 1,
    "water_heater__requested_state": WaterHeater.RequestedState.OFF,
    "water_heater__power": 2000,
    "water_heater__importance": LoadSheddingImportance.CRITICAL,
    "plan_requested_state": WaterHeater.RequestedState.ON,
}
PLAN_STATE_WANTS_OFF = {
    "water_heater_id": 2,
    "water_heater__requested_state": WaterHeater.RequestedState.ON,
    "water_heater__power": 2000,
    "water_heater__importance": LoadSheddingImportance.CRITICAL,
    "plan_requested_state": WaterHeater.RequestedState.OFF,
}
PLAN_STATE_ALREADY_ON = {
    "water_heater_id": 3,
    "water_heater__requested_state": WaterHeater.RequestedState.ON,
    "water_heater__power": 2000,
    "water_heater__importance": LoadSheddingImportance.CRITICAL,
    "plan_requested_state": WaterHeater.RequestedState.ON,
}
PLAN_STATE_LOAD_SHED_STAYS_SHED = {
    "water_heater_id": 4,
    "water_heater__requested_state": WaterHeater.RequestedState.LOAD_SHED,
    "water_heater__power": 2000,
    "water_heater__importance": LoadSheddingImportance.CRITICAL,
    "plan_requested_state": WaterHeater.RequestedState.ON,
}
PLAN_STATE_NO_OPINION = {
    "water_heater_id": 5,
    "water_heater__requested_state": WaterHeater.RequestedState.ON,
    "water_heater__power": 2000,
    "water_heater__importance": LoadSheddingImportance.CRITICAL,
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
        "to_turn_on": [
            {"id": 1, "power": 2000, "importance": LoadSheddingImportance.CRITICAL},
            {"id": 4, "power": 2000, "importance": LoadSheddingImportance.CRITICAL},
        ],
        "ids_to_turn_off": [2],
    }


def test_resolve_water_heaters_to_update_load_shed_is_requeued_for_retry():
    """A LOAD_SHED water heater whose plan still wants ON is put back in
    the to_turn_on queue (not forced directly to ON) — same self-healing
    retry mechanism as radiators: the listener decides, from there,
    whether there's now enough power to actually turn it back on."""
    result = resolve_water_heaters_to_update([PLAN_STATE_LOAD_SHED_STAYS_SHED])

    assert result == {
        "to_turn_on": [
            {"id": 4, "power": 2000, "importance": LoadSheddingImportance.CRITICAL}
        ],
        "ids_to_turn_off": [],
    }


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
            "to_turn_on": [
                {
                    "id": water_heater.id,
                    "power": 2000,
                    "importance": LoadSheddingImportance.CRITICAL,
                }
            ],
            "ids_to_turn_off": [],
        }
    )

    water_heater.refresh_from_db()
    # requested_state is NOT changed here
    assert water_heater.requested_state == WaterHeater.RequestedState.OFF
    # only added to the cache, for the teleinfo listener to decide
    assert get_water_heaters_to_turn_on_in_cache() == [
        {"id": water_heater.id, "power": 2000, "importance": LoadSheddingImportance.CRITICAL}
    ]


WATER_HEATER_1 = {
    "id": 1,
    "power": 2000,
    "importance": LoadSheddingImportance.CRITICAL,
}
WATER_HEATER_2 = {
    "id": 2,
    "power": 2000,
    "importance": LoadSheddingImportance.CRITICAL,
}
WATER_HEATER_3 = {
    "id": 3,
    "power": 2000,
    "importance": LoadSheddingImportance.CRITICAL,
}


@pytest.mark.django_db
def test_turn_on_water_heaters_according_to_the_available_power(mocker):
    mocker.patch("actuators.models.OnOffSwitch.turn_on")
    mocker.patch("actuators.models.OnOffSwitch.turn_off")
    mocker.patch("actuators.models.OnOffSwitch.read_state", return_value=False)
    water_heater_1 = WaterHeaterFactory(
        id=1, requested_state=WaterHeater.RequestedState.OFF
    )
    water_heater_2 = WaterHeaterFactory(
        id=2, requested_state=WaterHeater.RequestedState.OFF
    )
    water_heater_3 = WaterHeaterFactory(
        id=3, requested_state=WaterHeater.RequestedState.OFF
    )

    mocker.patch(
        "water_heater.services.water_heater_synchronization.get_water_heaters_to_turn_on_in_cache",
        return_value=[{"importance": LoadSheddingImportance.CRITICAL, "power": 1}],
    )

    can_turn_on = [WATER_HEATER_1, WATER_HEATER_2]
    cannot_turn_on = [WATER_HEATER_3]
    mocker.patch(
        "water_heater.services.water_heater_synchronization.split_by_available_power",
        return_value=(can_turn_on, cannot_turn_on),
    )

    result = turn_on_water_heaters_according_to_the_available_power(
        remaining_power=4000
    )

    # 4000 - (2000 + 2000) turned on
    assert result == 0
    assert get_water_heaters_to_turn_on_in_cache() == cannot_turn_on
    water_heater_1.refresh_from_db()
    water_heater_2.refresh_from_db()
    water_heater_3.refresh_from_db()

    assert water_heater_1.requested_state == WaterHeater.RequestedState.ON
    assert water_heater_2.requested_state == WaterHeater.RequestedState.ON
    assert water_heater_3.requested_state == WaterHeater.RequestedState.LOAD_SHED


@pytest.mark.django_db
@pytest.mark.parametrize("remaining_power", [None, 0, -100])
def test_turn_on_water_heaters_according_to_the_available_power_is_a_noop_when_nothing_can_turn_on(
    mocker, remaining_power
):
    mocked_get_cache = mocker.patch(
        "water_heater.services.water_heater_synchronization.get_water_heaters_to_turn_on_in_cache"
    )

    result = turn_on_water_heaters_according_to_the_available_power(
        remaining_power=remaining_power
    )

    mocked_get_cache.assert_not_called()
    # noop: the input power is returned unchanged
    assert result == remaining_power
