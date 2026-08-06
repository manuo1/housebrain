import pytest

from actuators.drivers.shelly import ShellyError
from equipment.models import PulseSwitch
from equipment.services.pulse_switch import (
    PULSE_SECONDS,
    PulseSwitchBusyError,
    PulseSwitchError,
    PulseSwitchService,
)
from equipment.tests.factories import PulseSwitchFactory


@pytest.mark.django_db
def test_trigger_success(mocker):
    pulse_switch = PulseSwitchFactory()
    mock_set_switch = mocker.patch(
        "equipment.services.pulse_switch.ShellyDriver.set_switch"
    )

    PulseSwitchService.trigger(pulse_switch.pk)

    mock_set_switch.assert_called_once_with(True, toggle_after=PULSE_SECONDS)
    pulse_switch.refresh_from_db()
    assert pulse_switch.status == PulseSwitch.Status.IDLE
    assert pulse_switch.last_triggered_at is not None


@pytest.mark.django_db
def test_trigger_already_in_progress_raises_busy_and_never_calls_driver(mocker):
    pulse_switch = PulseSwitchFactory(status=PulseSwitch.Status.IN_PROGRESS)
    mock_set_switch = mocker.patch(
        "equipment.services.pulse_switch.ShellyDriver.set_switch"
    )

    with pytest.raises(PulseSwitchBusyError):
        PulseSwitchService.trigger(pulse_switch.pk)

    mock_set_switch.assert_not_called()
    pulse_switch.refresh_from_db()
    # still IN_PROGRESS: a busy trigger must not touch/reset the lock
    assert pulse_switch.status == PulseSwitch.Status.IN_PROGRESS


@pytest.mark.django_db
def test_trigger_no_shelly_assigned_raises_and_never_locks(mocker):
    pulse_switch = PulseSwitchFactory(shelly=None)
    mock_set_switch = mocker.patch(
        "equipment.services.pulse_switch.ShellyDriver.set_switch"
    )

    with pytest.raises(PulseSwitchError, match="has no Shelly assigned"):
        PulseSwitchService.trigger(pulse_switch.pk)

    mock_set_switch.assert_not_called()
    pulse_switch.refresh_from_db()
    assert pulse_switch.status == PulseSwitch.Status.IDLE


@pytest.mark.django_db
def test_trigger_does_not_exist():
    with pytest.raises(PulseSwitchError, match="does not exist"):
        PulseSwitchService.trigger(999999)


@pytest.mark.django_db
def test_trigger_driver_error_still_releases_the_lock(mocker):
    pulse_switch = PulseSwitchFactory()
    mocker.patch(
        "equipment.services.pulse_switch.ShellyDriver.set_switch",
        side_effect=ShellyError("boom"),
    )

    with pytest.raises(PulseSwitchError, match="Unable to trigger"):
        PulseSwitchService.trigger(pulse_switch.pk)

    pulse_switch.refresh_from_db()
    # lock released via finally even though the driver call failed
    assert pulse_switch.status == PulseSwitch.Status.IDLE
    # and the pulse never actually happened, so no timestamp
    assert pulse_switch.last_triggered_at is None
