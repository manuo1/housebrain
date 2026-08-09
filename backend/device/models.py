from django.db import models

from device.catalog import DEVICE_MODELS, IOMode, get_device_model_spec


class Device(models.Model):
    """
    Base class for any physical, addressable device. Not tied to a
    transport (IP, I2C pin bus...) — that's the job of a concrete
    subclass, e.g. IPDevice. Owns DeviceIO rows via the `io` related_name.
    """

    reference = models.CharField(
        max_length=30,
        choices=[(key, key) for key in DEVICE_MODELS],
        verbose_name="Référence",
        help_text="Modèle exact du device (détermine ses IO et son driver)",
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
    )

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    def __str__(self):
        return self.name

    def get_model_spec(self):
        """Returns this device's DeviceModelSpec (IOs, driver class)."""
        return get_device_model_spec(self.reference)


class IPDevice(Device):
    """
    A Device reachable over IP (e.g. a Shelly 1 Mini Gen3). Multi-table
    inheritance: an IPDevice IS a Device, with an extra `ip` field — a
    future non-IP device (e.g. an MCP23017 addressed by I2C bus + pin)
    would be a sibling subclass of Device, not of IPDevice.
    """

    ip = models.GenericIPAddressField(
        protocol="IPv4",
        unique=True,
        verbose_name="Adresse IP",
        help_text="Adresse IP locale du device (réservée sur la box)",
    )

    class Meta:
        verbose_name = "Device IP"
        verbose_name_plural = "Devices IP"

    def __str__(self):
        return f"{self.name} ({self.ip})"


class DeviceIO(models.Model):
    """
    One physical input/output of a Device (e.g. a Shelly's relay or SW
    terminal; a future MCP23017 pin). FK to the base Device — deliberately
    not to IPDevice — so this model stays reusable for any transport.

    `key` matches an IOSpec.key from the device's model declaration — it's
    how code finds "the relay IO" or "the SW IO" for a given Device without
    hardcoding a positional index.

    NOTE: no FK to Actuator/Sensor yet — those don't exist as generic
    models in this codebase today (only concrete ones: actuators.Shelly,
    actuators.Radiator, sensors.TemperatureSensor). Linking an IO to an
    Equipment is deliberately left out of this first pass — see
    [[housebrain-device]].
    """

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="io",
        verbose_name="Device",
    )

    key = models.CharField(
        max_length=50,
        verbose_name="Clé",
        help_text="Identifiant stable de l'IO, tel que déclaré dans le modèle du device",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nom",
        help_text="Copié depuis la déclaration du modèle à la création du device",
    )

    mode = models.CharField(
        max_length=30,
        choices=IOMode.choices,
        default=IOMode.NOT_USED_IN_APP,
        verbose_name="Mode",
        help_text=(
            "Configuration actuelle de cette IO. Les choix affichés dans l'admin "
            "sont restreints à ceux compatibles avec le type de cette IO — voir "
            "device.catalog.IO_TYPE_ALLOWED_MODES."
        ),
    )

    class Meta:
        verbose_name = "IO"
        verbose_name_plural = "IO"
        constraints = [
            models.UniqueConstraint(
                fields=["device", "key"], name="unique_device_io_key"
            )
        ]

    def __str__(self):
        return f"{self.device.name} — {self.name}"

    def get_driver(self):
        """
        Returns a ready-to-use driver instance for this IO's device.
        Deliberately passes the base Device instance as-is — it's each
        driver's own job to resolve whatever subclass/fields it needs (e.g.
        ShellyDriver resolves an IPDevice for its `ip`). Keeps DeviceIO
        itself unaware of which Device subclasses exist.
        """
        driver_class = self.device.get_model_spec().get_driver_class()
        return driver_class(self.device)


class RelayOnOff(models.Model):
    """
    An on/off relay IO, ready for the app to control. Exists exactly while
    its DeviceIO.mode == RELAY_ON_OFF — created/deleted by the service that
    changes an IO's mode (see [[housebrain-device]]), never directly.
    """

    device_io = models.OneToOneField(
        DeviceIO,
        on_delete=models.CASCADE,
        related_name="relay_on_off",
        verbose_name="IO",
    )

    class Meta:
        verbose_name = "Relais on/off"
        verbose_name_plural = "Relais on/off"

    def __str__(self):
        return str(self.device_io)

    def turn_on(self) -> None:
        self.device_io.get_driver().set_io_output(self.device_io.key, on=True)

    def turn_off(self) -> None:
        self.device_io.get_driver().set_io_output(self.device_io.key, on=False)

    def pulse(self, seconds: float) -> None:
        """Turns on, and lets the device itself revert to off after `seconds`."""
        self.device_io.get_driver().set_io_output(self.device_io.key, on=True, pulse_seconds=seconds)


class SensorTrueFalse(models.Model):
    """
    A readable true/false sensor IO. Exists exactly while its
    DeviceIO.mode == SENSOR_TRUE_FALSE — created/deleted by the service
    that changes an IO's mode (see [[housebrain-device]]), never directly.
    """

    device_io = models.OneToOneField(
        DeviceIO,
        on_delete=models.CASCADE,
        related_name="sensor_true_false",
        verbose_name="IO",
    )

    class Meta:
        verbose_name = "Capteur (vrai/faux)"
        verbose_name_plural = "Capteurs (vrai/faux)"

    def __str__(self):
        return str(self.device_io)

    def read_state(self) -> bool:
        return self.device_io.get_driver().read_io_state(self.device_io.key)
