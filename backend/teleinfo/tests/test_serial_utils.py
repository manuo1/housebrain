import serial
from unittest.mock import patch, MagicMock
from teleinfo.serial_utils import get_serial_connection
from teleinfo.constants import SerialConfig


@patch("serial.Serial")
def test_get_serial_connection_success(mock_serial):
    mock_instance = MagicMock()
    # mocks the behavior of the `__enter__()` method used in a `with` statement
    mock_serial.return_value.__enter__.return_value = mock_instance
    mock_instance.readline.return_value = b"DATA_RECEIVED"
    assert get_serial_connection(SerialConfig) is not None


@patch("serial.Serial")
def test_get_serial_connection_no_data(mock_serial):
    mock_instance = MagicMock()
    mock_serial.return_value.__enter__.return_value = mock_instance
    mock_instance.readline.return_value = b""
    assert get_serial_connection(SerialConfig) is None


@patch("serial.Serial")
def test_get_serial_connection_serial_exception(mock_serial):
    mock_serial.side_effect = serial.SerialException()
    assert get_serial_connection(SerialConfig) is None
