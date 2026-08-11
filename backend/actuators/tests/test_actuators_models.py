from actuators.tests.factories import SingleButtonMotorFactory


def test_single_button_motor_trigger_delegates_to_relay_pulse(mocker):
    mock_pulse = mocker.patch("device.models.RelayOnOff.pulse")
    motor = SingleButtonMotorFactory.build(pulse_seconds=2.5)

    motor.trigger()

    mock_pulse.assert_called_once_with(2.5)
