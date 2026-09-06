import pytest
from django.core.management import call_command


def test_periodic_tasks_calls_all_steps_in_order(mocker):
    call_order = []

    mocker.patch(
        "scheduler.management.commands.periodic_tasks.save_teleinfo_data",
        side_effect=lambda: call_order.append("save_teleinfo_data"),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "synchronize_room_requested_heating_states_with_room_heating_day_plan",
        side_effect=lambda: call_order.append("sync_requested_heating_states"),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.resolve_radiators_to_update",
        side_effect=lambda: call_order.append("resolve_radiators_to_update")
        or {"ids_to_turn_off": [], "to_turn_on": []},
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "turn_off_radiators_and_apply_to_hardware",
        side_effect=lambda radiators_to_update: call_order.append(
            "turn_off_radiators_and_apply_to_hardware"
        ),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.queue_radiators_to_turn_on",
        side_effect=lambda radiators_to_update: call_order.append(
            "queue_radiators_to_turn_on"
        ),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.get_water_heaters_plan_states",
        side_effect=lambda: call_order.append("get_water_heaters_plan_states") or [],
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.resolve_water_heaters_to_update",
        side_effect=lambda plan_states: call_order.append(
            "resolve_water_heaters_to_update"
        )
        or {"ids_to_turn_off": [], "to_turn_on": []},
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "turn_off_water_heaters_and_apply_to_hardware",
        side_effect=lambda water_heaters_to_update: call_order.append(
            "turn_off_water_heaters_and_apply_to_hardware"
        ),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.queue_water_heaters_to_turn_on",
        side_effect=lambda water_heaters_to_update: call_order.append(
            "queue_water_heaters_to_turn_on"
        ),
    )
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.log_system_metrics",
        side_effect=lambda: call_order.append("log_system_metrics"),
    )

    call_command("periodic_tasks")

    assert call_order == [
        "save_teleinfo_data",
        "sync_requested_heating_states",
        "resolve_radiators_to_update",
        "turn_off_radiators_and_apply_to_hardware",
        "queue_radiators_to_turn_on",
        "get_water_heaters_plan_states",
        "resolve_water_heaters_to_update",
        "turn_off_water_heaters_and_apply_to_hardware",
        "queue_water_heaters_to_turn_on",
        "log_system_metrics",
    ]


def test_periodic_tasks_stops_and_raises_if_a_step_fails(mocker):
    """
    The command has no try/except around its steps: if one step raises,
    the exception propagates and the remaining steps are not executed.
    """
    mocker.patch(
        "scheduler.management.commands.periodic_tasks.save_teleinfo_data",
        side_effect=RuntimeError("boom"),
    )
    mock_sync = mocker.patch(
        "scheduler.management.commands.periodic_tasks."
        "synchronize_room_requested_heating_states_with_room_heating_day_plan"
    )

    with pytest.raises(RuntimeError):
        call_command("periodic_tasks")

    mock_sync.assert_not_called()
