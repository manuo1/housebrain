import pytest
from django.db import IntegrityError

from device.catalog import Shelly1MiniGen3
from device.drivers.shelly import ShellyDriver
from device.models import Device, DeviceIO
from device.tests.factories import DeviceIOFactory, IPDeviceFactory, RelayOnOffFactory, SensorTrueFalseFactory


@pytest.mark.django_db
def test_device_get_model_spec():
    device = IPDeviceFactory()

    assert device.get_model_spec() is Shelly1MiniGen3


@pytest.mark.django_db
def test_device_io_get_driver_returns_a_shelly_driver_bound_to_its_ip():
    ip_device = IPDeviceFactory(ip="192.168.1.42")
    device_io = DeviceIOFactory(device=ip_device, key="relay")

    driver = device_io.get_driver()

    assert isinstance(driver, ShellyDriver)
    assert driver.ip == "192.168.1.42"


@pytest.mark.django_db
def test_device_io_get_driver_receives_the_base_device_instance(mocker):
    # get_driver() must stay unaware of Device subclasses — it's each
    # driver's own job to resolve what it needs (see
    # test_device_drivers_shelly.test_init_resolves_ip_from_base_device_instance).
    #
    # Re-fetched from DB on purpose: a freshly-created device_io still
    # holds the exact IPDevice Python object it was assigned in this same
    # process (FK descriptor cache), which isn't representative of the
    # real call path (DeviceIOService always re-fetches DeviceIO fresh).
    ip_device = IPDeviceFactory()
    created = DeviceIOFactory(device=ip_device)
    device_io = DeviceIO.objects.get(pk=created.pk)
    mock_driver_class = mocker.patch("device.catalog.Shelly1MiniGen3.get_driver_class").return_value

    device_io.get_driver()

    passed_device = mock_driver_class.call_args.args[0]
    assert type(passed_device) is Device
    assert not hasattr(passed_device, "ip")


def test_relay_on_off_turn_on_delegates_to_driver(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    relay = RelayOnOffFactory.build(device_io=DeviceIO(key="relay"))

    relay.turn_on()

    mock_get_driver.return_value.set_io_output.assert_called_once_with("relay", on=True)


def test_relay_on_off_turn_off_delegates_to_driver(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    relay = RelayOnOffFactory.build(device_io=DeviceIO(key="relay"))

    relay.turn_off()

    mock_get_driver.return_value.set_io_output.assert_called_once_with("relay", on=False)


def test_relay_on_off_pulse_delegates_to_driver(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    relay = RelayOnOffFactory.build(device_io=DeviceIO(key="relay"))

    relay.pulse(1.5)

    mock_get_driver.return_value.set_io_output.assert_called_once_with(
        "relay", on=True, pulse_seconds=1.5
    )


def test_sensor_true_false_read_state_delegates_to_driver(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    mock_get_driver.return_value.read_io_state.return_value = True
    sensor = SensorTrueFalseFactory.build(device_io=DeviceIO(key="sw"))

    assert sensor.read_state() is True
    mock_get_driver.return_value.read_io_state.assert_called_once_with("sw")


@pytest.mark.django_db
def test_device_io_unique_key_per_device():
    ip_device = IPDeviceFactory()
    DeviceIOFactory(device=ip_device, key="relay")

    with pytest.raises(IntegrityError):
        DeviceIOFactory(device=ip_device, key="relay")
