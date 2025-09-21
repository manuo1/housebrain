# backend/actuators/tests/test_mcp23017.py
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch
import pytest

# ---------------------------
# Inject fake hardware modules
# ---------------------------
# Do this BEFORE importing the driver so import-time checks from 'board'
# or 'adafruit_blinka' won't fail on Windows.
fake_board = ModuleType("board")
# provide SCL / SDA placeholders so busio.I2C(board.SCL, board.SDA) won't fail
fake_board.SCL = object()
fake_board.SDA = object()
sys.modules["board"] = fake_board

fake_busio = ModuleType("busio")
# provide an I2C callable that returns a fake I2C object
fake_busio.I2C = MagicMock(return_value=MagicMock(name="I2C"))
sys.modules["busio"] = fake_busio

# create package and submodule for adafruit_mcp230xx.mcp23017
sys.modules["adafruit_mcp230xx"] = ModuleType("adafruit_mcp230xx")
fake_mcp_sub = ModuleType("adafruit_mcp230xx.mcp23017")
# placeholder class (will be patched in fixtures)
fake_mcp_sub.MCP23017 = MagicMock()
sys.modules["adafruit_mcp230xx.mcp23017"] = fake_mcp_sub

# ---------------------------
# Now import the module under test
# ---------------------------
import actuators.drivers.mcp23017 as mcp_module
from actuators.drivers.mcp23017 import MCP23017Driver, MCP23017Error, get_mcp_driver
from actuators.constants import MCP23017PinState


# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def mock_mcp():
    """
    Patch the MCP23017 class in the driver module to return a MagicMock instance.
    The returned mock instance has a `get_pin()` that returns a pin mock with
    .value and .switch_to_output() attributes.
    """
    with patch("actuators.drivers.mcp23017.MCP23017") as mock_cls:
        mock_instance = MagicMock(name="MCP23017_instance")
        mock_pin = MagicMock(name="MCP23017_pin")
        mock_pin.value = False
        mock_instance.get_pin.return_value = mock_pin
        mock_cls.return_value = mock_instance
        yield mock_instance


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the module-global singleton between tests."""
    mcp_module._mcp_driver = None
    yield
    mcp_module._mcp_driver = None


# ---------------------------
# Tests for normal mode (UNPLUGGED_MODE = False)
# ---------------------------
@pytest.mark.usefixtures("mock_mcp")
def test_set_pin_success(monkeypatch, mock_mcp):
    monkeypatch.setattr(mcp_module, "UNPLUGGED_MODE", False)

    driver = MCP23017Driver()
    # ensure the driver uses our mock MCP instance
    driver.mcp = mock_mcp
    pin = mock_mcp.get_pin.return_value

    pin.value = True  # simulated read matches requested state
    driver.set_pin(3, True)

    mock_mcp.get_pin.assert_called_with(3)
    pin.switch_to_output.assert_called_with(value=True)


@pytest.mark.usefixtures("mock_mcp")
def test_set_pin_state_mismatch(monkeypatch, mock_mcp):
    monkeypatch.setattr(mcp_module, "UNPLUGGED_MODE", False)

    driver = MCP23017Driver()
    driver.mcp = mock_mcp
    pin = mock_mcp.get_pin.return_value

    pin.value = False  # simulated read != requested state

    with pytest.raises(MCP23017Error) as excinfo:
        driver.set_pin(2, True)

    assert "incorrect" in str(excinfo.value)
    # In case of mismatch, driver sets pin_state to UNDEFINED
    assert excinfo.value.pin_state == MCP23017PinState.UNDEFINED


@pytest.mark.usefixtures("mock_mcp")
def test_get_pin_success(monkeypatch, mock_mcp):
    monkeypatch.setattr(mcp_module, "UNPLUGGED_MODE", False)

    driver = MCP23017Driver()
    driver.mcp = mock_mcp
    pin = mock_mcp.get_pin.return_value

    pin.value = True
    state = driver.get_pin(5)

    assert state is True
    mock_mcp.get_pin.assert_called_with(5)


@pytest.mark.usefixtures("mock_mcp")
def test_get_pin_error(monkeypatch, mock_mcp):
    monkeypatch.setattr(mcp_module, "UNPLUGGED_MODE", False)

    driver = MCP23017Driver()
    driver.mcp = mock_mcp
    mock_mcp.get_pin.side_effect = ValueError("bad pin")

    with pytest.raises(MCP23017Error) as excinfo:
        driver.get_pin(99)

    assert "MCP23017 error" in str(excinfo.value)


# ---------------------------
# Tests for UNPLUGGED_MODE = True (simulation)
# ---------------------------
def test_set_pin_unplugged(monkeypatch):
    monkeypatch.setattr(mcp_module, "UNPLUGGED_MODE", True)

    driver = MCP23017Driver()
    # in unplugged mode set_pin must not raise
    driver.set_pin(1, True)
    driver.set_pin(1, False)


def test_get_pin_unplugged(monkeypatch):
    monkeypatch.setattr(mcp_module, "UNPLUGGED_MODE", True)

    driver = MCP23017Driver()
    state = driver.get_pin(1)

    # default simulated state is False in the driver
    assert state is False


def test_global_driver_instance(monkeypatch, mock_mcp):
    monkeypatch.setattr(mcp_module, "UNPLUGGED_MODE", False)

    d1 = get_mcp_driver()
    d2 = get_mcp_driver()
    assert d1 is d2  # singleton
