from sensors.tests.factories import DoorContactSensorFactory


def test_door_contact_sensor_is_closed_when_true_and_closed_when_true(mocker):
    mocker.patch("device.models.SensorTrueFalse.read_state", return_value=True)
    sensor = DoorContactSensorFactory.build(closed_when_true=True)

    assert sensor.is_closed() is True


def test_door_contact_sensor_is_open_when_false_and_closed_when_true(mocker):
    mocker.patch("device.models.SensorTrueFalse.read_state", return_value=False)
    sensor = DoorContactSensorFactory.build(closed_when_true=True)

    assert sensor.is_closed() is False


def test_door_contact_sensor_is_closed_when_false_and_not_closed_when_true(mocker):
    mocker.patch("device.models.SensorTrueFalse.read_state", return_value=False)
    sensor = DoorContactSensorFactory.build(closed_when_true=False)

    assert sensor.is_closed() is True


def test_door_contact_sensor_is_open_when_true_and_not_closed_when_true(mocker):
    mocker.patch("device.models.SensorTrueFalse.read_state", return_value=True)
    sensor = DoorContactSensorFactory.build(closed_when_true=False)

    assert sensor.is_closed() is False


def test_door_contact_sensor_get_readable_state_closed(mocker):
    mocker.patch("sensors.models.DoorContactSensor.is_closed", return_value=True)
    sensor = DoorContactSensorFactory.build()

    assert sensor.get_readable_state() == "Porte fermée"


def test_door_contact_sensor_get_readable_state_open(mocker):
    mocker.patch("sensors.models.DoorContactSensor.is_closed", return_value=False)
    sensor = DoorContactSensorFactory.build()

    assert sensor.get_readable_state() == "Porte ouverte"
