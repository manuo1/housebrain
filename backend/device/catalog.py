"""
Declarative catalog of supported device models.

A DeviceModelSpec is the single source of truth for what a given device
reference (e.g. a Shelly 1 Mini Gen3) exposes physically: how many IOs it
has, what each is called and capable of, and which driver class knows how
to talk to it. The Device app uses this catalog to provision a Device's
DeviceIO rows and to instantiate the right driver — it never hardcodes
brand-specific knowledge itself.

Adding a new supported device model = add one DeviceModelSpec subclass
here (+ its driver under device/drivers/) and register it in
DEVICE_MODELS. Nothing above this layer (Device, DeviceIO, or whatever
ends up calling them) needs to change.
"""

from dataclasses import dataclass
from enum import StrEnum

from django.db import models


class IOType(StrEnum):
    """
    What an IO is capable of being used as, from the Device app's point of
    view — independent of the underlying protocol (an IP relay terminal
    and an MCP23017 pin can share the same IOType).
    """

    # Fixed-role output, always an actuator (e.g. a Shelly relay). Mode is
    # not configurable: a RELAY_ON_OFF IO has no sensor_enabled toggle.
    RELAY_ON_OFF = "relay_on_off"

    # Can be switched between "unused" and "sensor" (detached, readable
    # input). Never simultaneously acts as a manual switch for another
    # IO's relay — see IOMode below and DeviceIO.mode.
    SENSOR_TOGGLEABLE = "sensor_toggleable"


class IOMode(models.TextChoices):
    """
    Current configuration of a DeviceIO, chosen among whatever its IOType
    allows (see IO_TYPE_ALLOWED_MODES) — this is the instance-level state
    (device.models.DeviceIO.mode), as opposed to IOType which is the
    device model's fixed capability declaration. A Django TextChoices
    (not a plain StrEnum like IOType) since this one is actually stored in
    a model field — it carries the admin label alongside each value.
    """

    RELAY_ON_OFF = (
        "relay_on_off",
        "Relais on/off",
    )  # fixed mode of a RELAY_ON_OFF IO, never chosen by hand
    SENSOR_TRUE_FALSE = (
        "sensor_true_false",
        "Capteur (vrai/faux)",
    )  # a SENSOR_TOGGLEABLE IO, wired and read as a sensor
    NOT_USED_IN_APP = (
        "not_used_in_app",
        "Non utilisée dans l'app",
    )  # a SENSOR_TOGGLEABLE IO, left unused by the app (e.g. wired as a manual switch instead)


# Which IOMode values are valid for a given IOType, and which one a newly
# provisioned IO of that type gets by default. Used by the admin to
# restrict the `mode` choices shown for a given DeviceIO instance.
IO_TYPE_ALLOWED_MODES: dict[IOType, tuple[IOMode, ...]] = {
    IOType.RELAY_ON_OFF: (IOMode.RELAY_ON_OFF,),
    IOType.SENSOR_TOGGLEABLE: (IOMode.SENSOR_TRUE_FALSE, IOMode.NOT_USED_IN_APP),
}

IO_TYPE_DEFAULT_MODE: dict[IOType, IOMode] = {
    IOType.RELAY_ON_OFF: IOMode.RELAY_ON_OFF,
    IOType.SENSOR_TOGGLEABLE: IOMode.NOT_USED_IN_APP,
}


@dataclass(frozen=True)
class IOSpec:
    """One IO exposed by a device model, as declared below."""

    key: str  # stable id, matches a DeviceIO.key row for this device
    name: str  # human label, copied to DeviceIO.name at provisioning
    type: IOType


class DeviceModelSpec:
    """
    Base class for a device model declaration. Subclass once per supported
    device reference and register the subclass in DEVICE_MODELS below.
    Not meant to be instantiated — every attribute here is class-level.
    """

    reference: str
    ios: list[IOSpec]

    @classmethod
    def get_driver_class(cls):
        """Returns the DeviceDriver subclass that knows how to talk to this model."""
        raise NotImplementedError

    @classmethod
    def get_io_spec(cls, key: str) -> IOSpec:
        """Returns this model's IOSpec matching `key` (a DeviceIO.key)."""
        io_spec = next((io for io in cls.ios if io.key == key), None)
        if io_spec is None:
            raise ValueError(f"Unknown IO key {key!r} for {cls.reference!r}")
        return io_spec


class Shelly1MiniGen3(DeviceModelSpec):
    """
    Single-relay Shelly Gen2+ device. The SW IO can only ever be a
    detached sensor or unused — it is never a second actuator, and while
    detached it can no longer also serve as a manual switch for the relay
    (mutually exclusive by wiring, not just by software mode).
    """

    reference = "SHELLY_1_MINI_GEN3"

    ios = [
        IOSpec(key="relay", name="Relais", type=IOType.RELAY_ON_OFF),
        IOSpec(key="sw", name="SW", type=IOType.SENSOR_TOGGLEABLE),
    ]

    @classmethod
    def get_driver_class(cls):
        # Local import: device.drivers.shelly imports IOType/DeviceDriver
        # from this module's neighbours, so importing it at module level
        # here would create a circular import.
        from device.drivers.shelly import ShellyDriver

        return ShellyDriver


DEVICE_MODELS: dict[str, type[DeviceModelSpec]] = {
    Shelly1MiniGen3.reference: Shelly1MiniGen3,
}


def get_device_model_spec(reference: str) -> type[DeviceModelSpec]:
    try:
        return DEVICE_MODELS[reference]
    except KeyError:
        raise ValueError(f"Unsupported device reference: {reference!r}")
