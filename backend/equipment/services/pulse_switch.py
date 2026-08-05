import logging

from django.utils import timezone

from actuators.drivers.shelly import ShellyDriver, ShellyError
from core.constants import LoggerLabel
from equipment.models import PulseSwitch

logger = logging.getLogger("django")

# Momentary pulse duration sent to the Shelly (toggle_after), in seconds —
# hardcoded here rather than a DB field: this is the behavior of a
# PulseSwitch by definition, not a per-instance configuration choice.
PULSE_SECONDS = 1


class PulseSwitchError(Exception):
    """Exception for PulseSwitch service errors"""


class PulseSwitchBusyError(PulseSwitchError):
    """Raised when a trigger is already in progress for this PulseSwitch"""


class PulseSwitchService:
    """
    Service to trigger a PulseSwitch. Execution is synchronous (no periodic
    task involved, unlike Radiator) — the caller waits for the Shelly RPC
    call to complete, since a multi-second delay would be unacceptable for
    e.g. a garage door.
    """

    @staticmethod
    def trigger(pulse_switch_id: int) -> None:
        try:
            pulse_switch = PulseSwitch.objects.select_related("shelly").get(
                pk=pulse_switch_id
            )
        except PulseSwitch.DoesNotExist:
            raise PulseSwitchError(f"PulseSwitch {pulse_switch_id} does not exist")

        if pulse_switch.shelly is None:
            raise PulseSwitchError(
                f"PulseSwitch {pulse_switch_id} has no Shelly assigned"
            )

        # Atomic conditional update: a single UPDATE ... WHERE status=IDLE
        # statement, so concurrent gunicorn workers racing on the same
        # PulseSwitch can only have one of them actually win this lock —
        # the DB itself serializes the write, no explicit select_for_update
        # needed.
        locked = PulseSwitch.objects.filter(
            pk=pulse_switch_id, status=PulseSwitch.Status.IDLE
        ).update(status=PulseSwitch.Status.IN_PROGRESS)

        if not locked:
            raise PulseSwitchBusyError(
                f"PulseSwitch {pulse_switch_id} is already in progress"
            )

        try:
            ShellyDriver(pulse_switch.shelly).set_switch(
                True, toggle_after=PULSE_SECONDS
            )
            PulseSwitch.objects.filter(pk=pulse_switch_id).update(
                last_triggered_at=timezone.now()
            )
        except ShellyError as e:
            logger.error(
                f"{LoggerLabel.PULSESWITCH} Unable to trigger PulseSwitch "
                f"{pulse_switch_id} - {e}"
            )
            raise PulseSwitchError(
                f"Unable to trigger PulseSwitch {pulse_switch_id}: {e}"
            )
        finally:
            # Always release the lock, whether the pulse succeeded or not —
            # a stuck IN_PROGRESS would permanently block this PulseSwitch.
            PulseSwitch.objects.filter(pk=pulse_switch_id).update(
                status=PulseSwitch.Status.IDLE
            )
