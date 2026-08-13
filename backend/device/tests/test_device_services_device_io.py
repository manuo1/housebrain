import pytest

from actuators.tests.factories import SingleButtonMotorFactory
from device.catalog import IOMode
from device.drivers.base import DeviceDriverError
from device.models import RelayOnOff, SensorTrueFalse
from device.services.device_io import DeviceIOError, DeviceIOService
from device.tests.factories import DeviceIOFactory, IPDeviceFactory, RelayOnOffFactory, SensorTrueFalseFactory
from equipment.tests.factories import GarageDoorFactory
from sensors.tests.factories import DoorContactSensorFactory


# ---------------------------
# provision_device
# ---------------------------
@pytest.mark.django_db
def test_provision_device_creates_expected_ios(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    device = IPDeviceFactory()

    DeviceIOService.provision_device(device)

    ios = {io.key: io for io in device.io.all()}
    assert set(ios) == {"relay", "sw"}
    assert ios["relay"].mode == IOMode.RELAY_ON_OFF
    assert ios["sw"].mode == IOMode.NOT_USED_IN_APP
    mock_get_driver.assert_not_called()


@pytest.mark.django_db
def test_provision_device_creates_relay_on_off_for_the_relay_only():
    device = IPDeviceFactory()

    DeviceIOService.provision_device(device)

    ios = {io.key: io for io in device.io.all()}
    assert hasattr(ios["relay"], "relay_on_off")
    # SW starts NOT_USED_IN_APP: no SensorTrueFalse row until set_io_mode()
    # is used to turn it into a sensor.
    assert not hasattr(ios["sw"], "sensor_true_false")


# ---------------------------
# set_io_mode — happy paths
# ---------------------------
@pytest.mark.django_db
def test_set_io_mode_to_sensor_creates_row_and_calls_driver(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    device_io = DeviceIOFactory(key="sw", name="SW", mode=IOMode.NOT_USED_IN_APP)

    DeviceIOService.set_io_mode(device_io.pk, IOMode.SENSOR_TRUE_FALSE)

    device_io.refresh_from_db()
    assert device_io.mode == IOMode.SENSOR_TRUE_FALSE
    assert SensorTrueFalse.objects.filter(device_io=device_io).exists()
    mock_get_driver.return_value.set_sensor_mode.assert_called_once_with("sw", enabled=True)


@pytest.mark.django_db
def test_set_io_mode_to_unused_deletes_row_and_calls_driver(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    sensor = SensorTrueFalseFactory()
    device_io = sensor.device_io

    DeviceIOService.set_io_mode(device_io.pk, IOMode.NOT_USED_IN_APP)

    device_io.refresh_from_db()
    assert device_io.mode == IOMode.NOT_USED_IN_APP
    assert not SensorTrueFalse.objects.filter(device_io=device_io).exists()
    mock_get_driver.return_value.set_sensor_mode.assert_called_once_with("sw", enabled=False)


@pytest.mark.django_db
def test_set_io_mode_same_as_current_is_a_noop(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    device_io = DeviceIOFactory(key="sw", mode=IOMode.NOT_USED_IN_APP)

    DeviceIOService.set_io_mode(device_io.pk, IOMode.NOT_USED_IN_APP)

    mock_get_driver.assert_not_called()


# ---------------------------
# set_io_mode — errors
# ---------------------------
@pytest.mark.django_db
def test_set_io_mode_does_not_exist():
    with pytest.raises(DeviceIOError, match="does not exist"):
        DeviceIOService.set_io_mode(999999, IOMode.SENSOR_TRUE_FALSE)


@pytest.mark.django_db
def test_set_io_mode_rejects_a_mode_not_allowed_for_this_io_type(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    relay = RelayOnOffFactory()

    with pytest.raises(DeviceIOError, match="is not allowed"):
        DeviceIOService.set_io_mode(relay.device_io.pk, IOMode.SENSOR_TRUE_FALSE)

    mock_get_driver.assert_not_called()
    assert RelayOnOff.objects.filter(device_io=relay.device_io).exists()


@pytest.mark.django_db
def test_set_io_mode_driver_failure_rolls_back(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    mock_get_driver.return_value.set_sensor_mode.side_effect = DeviceDriverError("unreachable")
    sensor = SensorTrueFalseFactory()
    device_io = sensor.device_io

    with pytest.raises(DeviceIOError, match="Unable to set mode"):
        DeviceIOService.set_io_mode(device_io.pk, IOMode.NOT_USED_IN_APP)

    device_io.refresh_from_db()
    # @transaction.atomic: the row deletion that happened before the failed
    # driver call must be rolled back along with everything else.
    assert device_io.mode == IOMode.SENSOR_TRUE_FALSE
    assert SensorTrueFalse.objects.filter(device_io=device_io).exists()


@pytest.mark.django_db
def test_set_io_mode_refuses_when_sensor_is_linked_downstream(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    door_sensor = DoorContactSensorFactory()
    device_io = door_sensor.sensor_true_false.device_io

    with pytest.raises(DeviceIOError, match="still in use"):
        DeviceIOService.set_io_mode(device_io.pk, IOMode.NOT_USED_IN_APP)

    mock_get_driver.assert_not_called()
    device_io.refresh_from_db()
    assert device_io.mode == IOMode.SENSOR_TRUE_FALSE
    assert SensorTrueFalse.objects.filter(device_io=device_io).exists()


@pytest.mark.django_db
def test_set_io_mode_refuses_when_sensor_is_linked_to_a_full_garage_door(mocker):
    mock_get_driver = mocker.patch("device.models.DeviceIO.get_driver")
    garage_door = GarageDoorFactory()
    device_io = garage_door.door_sensor.sensor_true_false.device_io

    with pytest.raises(DeviceIOError, match="still in use"):
        DeviceIOService.set_io_mode(device_io.pk, IOMode.NOT_USED_IN_APP)

    mock_get_driver.assert_not_called()


# ---------------------------
# is_device_deletable
# ---------------------------
@pytest.mark.django_db
def test_is_device_deletable_true_for_a_freshly_provisioned_device():
    device = IPDeviceFactory()
    DeviceIOService.provision_device(device)

    assert DeviceIOService.is_device_deletable(device) is True


@pytest.mark.django_db
def test_is_device_deletable_false_when_relay_has_an_orphan_motor():
    relay = RelayOnOffFactory()
    SingleButtonMotorFactory(relay_on_off=relay)

    assert DeviceIOService.is_device_deletable(relay.device_io.device) is False


@pytest.mark.django_db
def test_is_device_deletable_false_when_sensor_has_an_orphan_door_sensor():
    door_sensor = DoorContactSensorFactory()

    assert DeviceIOService.is_device_deletable(door_sensor.sensor_true_false.device_io.device) is False


@pytest.mark.django_db
def test_is_device_deletable_false_for_a_full_garage_door():
    garage_door = GarageDoorFactory()

    device = garage_door.motor.relay_on_off.device_io.device

    assert DeviceIOService.is_device_deletable(device) is False
