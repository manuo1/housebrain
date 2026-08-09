import pytest

from device.catalog import (
    IO_TYPE_ALLOWED_MODES,
    IO_TYPE_DEFAULT_MODE,
    IOMode,
    IOType,
    Shelly1MiniGen3,
    get_device_model_spec,
)


def test_get_device_model_spec_known_reference():
    assert get_device_model_spec("SHELLY_1_MINI_GEN3") is Shelly1MiniGen3


def test_get_device_model_spec_unknown_reference():
    with pytest.raises(ValueError, match="Unsupported device reference"):
        get_device_model_spec("SOME_OTHER_MODEL")


def test_shelly_1_mini_gen3_declares_relay_and_sw():
    keys = {io.key for io in Shelly1MiniGen3.ios}
    assert keys == {"relay", "sw"}


def test_get_io_spec_known_key():
    io_spec = Shelly1MiniGen3.get_io_spec("relay")
    assert io_spec.type == IOType.RELAY_ON_OFF


def test_get_io_spec_unknown_key():
    with pytest.raises(ValueError, match="Unknown IO key"):
        Shelly1MiniGen3.get_io_spec("nope")


def test_get_driver_class_returns_shelly_driver():
    from device.drivers.shelly import ShellyDriver

    assert Shelly1MiniGen3.get_driver_class() is ShellyDriver


def test_io_type_allowed_modes_covers_every_io_type():
    assert set(IO_TYPE_ALLOWED_MODES) == set(IOType)


def test_relay_on_off_only_allows_itself():
    assert IO_TYPE_ALLOWED_MODES[IOType.RELAY_ON_OFF] == (IOMode.RELAY_ON_OFF,)


def test_sensor_toggleable_allows_sensor_or_unused():
    assert set(IO_TYPE_ALLOWED_MODES[IOType.SENSOR_TOGGLEABLE]) == {
        IOMode.SENSOR_TRUE_FALSE,
        IOMode.NOT_USED_IN_APP,
    }


def test_default_mode_is_always_allowed_for_its_type():
    for io_type, default_mode in IO_TYPE_DEFAULT_MODE.items():
        assert default_mode in IO_TYPE_ALLOWED_MODES[io_type]
