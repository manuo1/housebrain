import factory

from device.catalog import IOMode, Shelly1MiniGen3
from device.models import DeviceIO, IPDevice, RelayOnOff, SensorTrueFalse


class IPDeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IPDevice

    name = factory.Sequence(lambda n: f"Device {n}")
    reference = Shelly1MiniGen3.reference
    ip = factory.Sequence(lambda n: f"192.168.1.{n % 254 + 1}")


class DeviceIOFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeviceIO

    device = factory.SubFactory(IPDeviceFactory)
    key = "relay"
    name = "Relais"
    mode = IOMode.NOT_USED_IN_APP


class RelayOnOffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RelayOnOff

    device_io = factory.SubFactory(DeviceIOFactory, key="relay", name="Relais", mode=IOMode.RELAY_ON_OFF)


class SensorTrueFalseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SensorTrueFalse

    device_io = factory.SubFactory(
        DeviceIOFactory, key="sw", name="SW", mode=IOMode.SENSOR_TRUE_FALSE
    )
