import logging

from django.db import transaction

from core.constants import LoggerLabel
from device.catalog import IO_TYPE_ALLOWED_MODES, IO_TYPE_DEFAULT_MODE, IOMode
from device.drivers.base import DeviceDriverError
from device.models import Device, DeviceIO, RelayOnOff, SensorTrueFalse

logger = logging.getLogger("django")


class DeviceIOError(Exception):
    """Exception for DeviceIO service errors"""


class DeviceIOService:
    """Service to provision a Device's IOs, and to change a DeviceIO's mode, keeping RelayOnOff/SensorTrueFalse in sync with it."""

    @staticmethod
    @transaction.atomic
    def provision_device(device: Device) -> None:
        """
        Creates this device's DeviceIO rows (and a RelayOnOff row for any
        fixed-role relay IO) from its DeviceModelSpec. Called once, right
        after a Device is created.

        Never touches the driver: every IO starts in its IOType's default
        mode (IO_TYPE_DEFAULT_MODE), which for a SENSOR_TOGGLEABLE IO is
        NOT_USED_IN_APP — matching the device's factory wiring (e.g. a
        Shelly's SW terminal defaults to "follow" the relay, not detached),
        so provisioning never needs to reach the device over the network.
        Switching an IO to SENSOR_TRUE_FALSE afterwards goes through
        set_io_mode() below, which does call the driver.
        """
        spec = device.get_model_spec()
        for io_spec in spec.ios:
            default_mode = IO_TYPE_DEFAULT_MODE[io_spec.type]
            device_io = DeviceIO.objects.create(
                device=device, key=io_spec.key, name=io_spec.name, mode=default_mode
            )
            if default_mode == IOMode.RELAY_ON_OFF:
                RelayOnOff.objects.create(device_io=device_io)

    @staticmethod
    @transaction.atomic
    def set_io_mode(device_io_id: int, new_mode: IOMode) -> None:
        """
        Raises:
            DeviceIOError: if the DeviceIO doesn't exist, new_mode isn't
                allowed for this IO's type, or the driver call fails
        """
        try:
            # select_for_update: prevents two concurrent callers from both
            # reading the same "old" mode and racing on which RelayOnOff/
            # SensorTrueFalse row ends up created — mirrors the DB-level
            # locking approach already used in PulseSwitchService.
            device_io = DeviceIO.objects.select_for_update().get(pk=device_io_id)
        except DeviceIO.DoesNotExist:
            raise DeviceIOError(f"DeviceIO {device_io_id} does not exist")

        if new_mode == device_io.mode:
            return

        try:
            io_spec = device_io.device.get_model_spec().get_io_spec(device_io.key)
        except ValueError as e:
            raise DeviceIOError(str(e))

        if new_mode not in IO_TYPE_ALLOWED_MODES[io_spec.type]:
            raise DeviceIOError(
                f"Mode {new_mode} is not allowed for DeviceIO {device_io_id} "
                f"(type {io_spec.type})"
            )

        # TODO once Equipment points to RelayOnOff/SensorTrueFalse instead
        # of directly to actuators.Shelly: refuse here if the row about to
        # be deleted below is still linked to an Equipment, instead of
        # silently deleting it — see [[housebrain-device]].
        if device_io.mode == IOMode.SENSOR_TRUE_FALSE:
            SensorTrueFalse.objects.filter(device_io=device_io).delete()
        elif device_io.mode == IOMode.RELAY_ON_OFF:
            # Not reachable today: a RELAY_ON_OFF-type IO's only allowed
            # mode is RELAY_ON_OFF itself (IO_TYPE_ALLOWED_MODES), so
            # new_mode == device_io.mode would already have returned above.
            # Kept for symmetry, in case a future IOType allows it to change.
            RelayOnOff.objects.filter(device_io=device_io).delete()

        try:
            device_io.get_driver().set_sensor_mode(
                device_io.key, enabled=(new_mode == IOMode.SENSOR_TRUE_FALSE)
            )
        except DeviceDriverError as e:
            logger.error(
                f"{LoggerLabel.DEVICEIO} Unable to set mode {new_mode} on "
                f"DeviceIO {device_io_id} - {e}"
            )
            raise DeviceIOError(f"Unable to set mode on DeviceIO {device_io_id}: {e}")

        device_io.mode = new_mode
        device_io.save(update_fields=["mode"])

        if new_mode == IOMode.SENSOR_TRUE_FALSE:
            SensorTrueFalse.objects.create(device_io=device_io)
        elif new_mode == IOMode.RELAY_ON_OFF:
            RelayOnOff.objects.create(device_io=device_io)
