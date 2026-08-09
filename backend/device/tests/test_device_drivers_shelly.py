import hashlib

import pytest
import requests

from device.drivers.shelly import ShellyDriver, ShellyError
from device.models import Device, IPDevice
from device.tests.factories import IPDeviceFactory


@pytest.fixture
def ip_device():
    # Unsaved instance: the driver only reads .reference/.ip, no DB needed.
    return IPDevice(
        name="Test Shelly",
        ip="192.168.1.50",
        reference="SHELLY_1_MINI_GEN3",
    )


@pytest.fixture(autouse=True)
def shelly_auth_password(settings):
    settings.SHELLY_AUTH_PASSWORD = "secret"


def _mock_response(mocker, json_data, status_code=200):
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# ---------------------------
# __init__ / reference guard / IPDevice resolution
# ---------------------------
def test_init_rejects_unsupported_reference():
    unsupported = IPDevice(name="x", ip="1.2.3.4", reference="SOME_OTHER_MODEL")

    with pytest.raises(ShellyError, match="Unsupported device reference"):
        ShellyDriver(unsupported)


def test_init_accepts_ip_device_instance_directly(ip_device):
    assert ShellyDriver(ip_device).ip == "192.168.1.50"


@pytest.mark.django_db
def test_init_resolves_ip_from_base_device_instance():
    # The real caller (DeviceIO.get_driver()) only ever has a base Device
    # instance in hand — this is the polymorphism case that motivated
    # keeping the IP resolution inside the driver, not in DeviceIO.
    saved = IPDeviceFactory(ip="192.168.1.77")
    base_device = Device.objects.get(pk=saved.pk)

    assert ShellyDriver(base_device).ip == "192.168.1.77"


# ---------------------------
# read_io_state
# ---------------------------
def test_read_io_state_relay(mocker, ip_device):
    mock_post = mocker.patch(
        "device.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {"output": True}}),
    )

    assert ShellyDriver(ip_device).read_io_state("relay") is True
    assert mock_post.call_args.kwargs["json"]["method"] == "Switch.GetStatus"


def test_read_io_state_sw(mocker, ip_device):
    mocker.patch(
        "device.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {"state": False}}),
    )

    assert ShellyDriver(ip_device).read_io_state("sw") is False


def test_read_io_state_unknown_key(ip_device):
    with pytest.raises(ShellyError, match="Unknown io_key"):
        ShellyDriver(ip_device).read_io_state("nope")


# ---------------------------
# set_io_output
# ---------------------------
def test_set_io_output_without_pulse(mocker, ip_device):
    mock_post = mocker.patch(
        "device.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {}}),
    )

    ShellyDriver(ip_device).set_io_output("relay", True)

    payload = mock_post.call_args.kwargs["json"]
    assert payload["method"] == "Switch.Set"
    assert payload["params"] == {"id": 0, "on": True}


def test_set_io_output_with_pulse(mocker, ip_device):
    mock_post = mocker.patch(
        "device.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {}}),
    )

    ShellyDriver(ip_device).set_io_output("relay", True, pulse_seconds=1)

    payload = mock_post.call_args.kwargs["json"]
    assert payload["params"] == {"id": 0, "on": True, "toggle_after": 1}


def test_set_io_output_on_non_output_key_raises(ip_device):
    with pytest.raises(ShellyError, match="is not an output IO"):
        ShellyDriver(ip_device).set_io_output("sw", True)


# ---------------------------
# set_sensor_mode
# ---------------------------
def test_set_sensor_mode_enabled_configures_detached_sensor(mocker, ip_device):
    mock_post = mocker.patch(
        "device.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {}}),
    )

    ShellyDriver(ip_device).set_sensor_mode("sw", enabled=True)

    switch_call, input_call = mock_post.call_args_list
    assert switch_call.kwargs["json"]["params"] == {
        "id": 0,
        "config": {"in_mode": "detached", "initial_state": "off"},
    }
    assert input_call.kwargs["json"]["params"] == {"id": 0, "config": {"type": "switch"}}


def test_set_sensor_mode_disabled_reverts_to_relay_switch(mocker, ip_device):
    mock_post = mocker.patch(
        "device.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {}}),
    )

    ShellyDriver(ip_device).set_sensor_mode("sw", enabled=False)

    switch_call, _ = mock_post.call_args_list
    assert switch_call.kwargs["json"]["params"] == {
        "id": 0,
        "config": {"in_mode": "follow", "initial_state": "match_input"},
    }


def test_set_sensor_mode_on_non_sensor_key_raises(ip_device):
    with pytest.raises(ShellyError, match="does not support sensor mode"):
        ShellyDriver(ip_device).set_sensor_mode("relay", enabled=True)


# ---------------------------
# set_auth
# ---------------------------
DEVICE_ID = "shellyplus1minig3-abc123"


def test_set_auth_success(mocker, ip_device):
    responses = [
        _mock_response(mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": False}}),
        _mock_response(mocker, {"id": 1, "result": {}}),
        _mock_response(mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": True}}),
    ]
    mock_post = mocker.patch("device.drivers.shelly.requests.post", side_effect=responses)

    ShellyDriver(ip_device).set_auth("my-password")

    setauth_payload = mock_post.call_args_list[1].kwargs["json"]
    assert setauth_payload["method"] == "Shelly.SetAuth"
    expected_ha1 = hashlib.sha256(f"admin:{DEVICE_ID}:my-password".encode()).hexdigest()
    assert setauth_payload["params"] == {
        "user": "admin",
        "realm": DEVICE_ID,
        "ha1": expected_ha1,
    }


def test_set_auth_raises_if_still_disabled_afterwards(mocker, ip_device):
    responses = [
        _mock_response(mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": False}}),
        _mock_response(mocker, {"id": 1, "result": {}}),
        _mock_response(mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": False}}),
    ]
    mocker.patch("device.drivers.shelly.requests.post", side_effect=responses)

    with pytest.raises(ShellyError, match="still reports auth disabled"):
        ShellyDriver(ip_device).set_auth("my-password")


# ---------------------------
# _rpc_call error handling
# ---------------------------
def test_rpc_call_timeout(mocker, ip_device):
    mocker.patch(
        "device.drivers.shelly.requests.post",
        side_effect=requests.exceptions.Timeout("timed out"),
    )

    with pytest.raises(ShellyError, match="timeout"):
        ShellyDriver(ip_device).read_io_state("relay")


def test_rpc_call_401_gives_actionable_message(mocker, ip_device):
    resp = mocker.MagicMock()
    resp.status_code = 401
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=resp)
    mocker.patch("device.drivers.shelly.requests.post", return_value=resp)

    with pytest.raises(ShellyError, match=r"rejected authentication \(401\)"):
        ShellyDriver(ip_device).read_io_state("relay")


def test_rpc_call_http_error_other_status(mocker, ip_device):
    resp = mocker.MagicMock()
    resp.status_code = 500
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=resp)
    mocker.patch("device.drivers.shelly.requests.post", return_value=resp)

    with pytest.raises(ShellyError, match="HTTP error"):
        ShellyDriver(ip_device).read_io_state("relay")


def test_rpc_call_connection_error(mocker, ip_device):
    mocker.patch(
        "device.drivers.shelly.requests.post",
        side_effect=requests.exceptions.ConnectionError("refused"),
    )

    with pytest.raises(ShellyError, match="error on"):
        ShellyDriver(ip_device).read_io_state("relay")


def test_rpc_call_error_in_response_body(mocker, ip_device):
    mocker.patch(
        "device.drivers.shelly.requests.post",
        return_value=_mock_response(
            mocker, {"id": 1, "error": {"code": -103, "message": "Invalid argument"}}
        ),
    )

    with pytest.raises(ShellyError, match="RPC error"):
        ShellyDriver(ip_device).read_io_state("relay")


def test_missing_password_raises_before_any_call(mocker, ip_device, settings):
    settings.SHELLY_AUTH_PASSWORD = None
    mock_post = mocker.patch("device.drivers.shelly.requests.post")

    with pytest.raises(ShellyError, match="SHELLY_AUTH_PASSWORD"):
        ShellyDriver(ip_device).read_io_state("relay")

    mock_post.assert_not_called()
