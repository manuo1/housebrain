"""
Abstract interface every device driver must implement. Code above the
Device app talks to a device only through this interface — never through a
brand-specific driver class directly — so that adding a new device model
(a different relay+sensor brand, say) never requires touching Device,
DeviceIO, or any of their callers.
"""

from abc import ABC, abstractmethod


class DeviceDriverError(Exception):
    """Base exception for any device driver error (network, protocol, or device-side)."""


class DeviceDriver(ABC):
    """
    One instance = one physical device. Every method takes an io_key
    matching an IOSpec.key from the device's DeviceModelSpec — the driver
    maps that key to whatever the real protocol needs (a relay id, a pin
    number, etc).
    """

    @abstractmethod
    def __init__(self, device):
        """device: a device.models.Device instance (or a concrete subclass, e.g. IPDevice)."""

    @abstractmethod
    def read_io_state(self, io_key: str) -> bool:
        """
        Read the current boolean state of an IO — the relay output for an
        actuator IO, or the input contact for a sensor IO.
        Raises:
            DeviceDriverError: on communication or device error
        """

    @abstractmethod
    def set_io_output(
        self, io_key: str, on: bool, pulse_seconds: float | None = None
    ) -> None:
        """
        Drive an output (actuator) IO.
        Args:
            on: True to turn on, False to turn off
            pulse_seconds: if set, the device reverts to the opposite state
                by itself after this many seconds (momentary/pulse command,
                e.g. a garage door impulse) — no follow-up call needed
        Raises:
            DeviceDriverError: on communication or device error
        """

    @abstractmethod
    def set_sensor_mode(self, io_key: str, enabled: bool) -> None:
        """
        Enable or disable sensor (detached) mode on a SENSOR_TOGGLEABLE IO.
        Has no meaning on a RELAY_ON_OFF IO.
        Raises:
            DeviceDriverError: on communication or device error
        """
