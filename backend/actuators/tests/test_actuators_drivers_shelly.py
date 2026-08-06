# backend/actuators/tests/test_actuators_drivers_shelly.py
import hashlib

import pytest
import requests

from actuators.drivers.shelly import ShellyDriver, ShellyError
from actuators.models import Shelly


@pytest.fixture
def shelly():
    # Unsaved instance: the driver only reads .reference/.ip, no DB needed.
    return Shelly(
        name="Test Shelly",
        ip="192.168.1.50",
        reference=Shelly.Reference.SHELLY_1_MINI_GEN3,
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
# __init__ / reference guard
# ---------------------------
def test_init_rejects_unsupported_reference():
    unsupported = Shelly(name="x", ip="1.2.3.4", reference="SOME_OTHER_MODEL")

    with pytest.raises(ShellyError, match="Unsupported Shelly reference"):
        ShellyDriver(unsupported)


# ---------------------------
# set_switch / get_switch_status
# ---------------------------
def test_set_switch_without_toggle_after(mocker, shelly):
    mock_post = mocker.patch(
        "actuators.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {"was_on": False}}),
    )

    ShellyDriver(shelly).set_switch(True)

    payload = mock_post.call_args.kwargs["json"]
    assert payload["method"] == "Switch.Set"
    assert payload["params"] == {"id": 0, "on": True}


def test_set_switch_with_toggle_after(mocker, shelly):
    mock_post = mocker.patch(
        "actuators.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {"was_on": False}}),
    )

    ShellyDriver(shelly).set_switch(True, toggle_after=1)

    payload = mock_post.call_args.kwargs["json"]
    assert payload["params"] == {"id": 0, "on": True, "toggle_after": 1}


def test_get_switch_status(mocker, shelly):
    mocker.patch(
        "actuators.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {"output": True}}),
    )

    assert ShellyDriver(shelly).get_switch_status() is True


# ---------------------------
# get_input_status
# ---------------------------
def test_get_input_status(mocker, shelly):
    mocker.patch(
        "actuators.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {"state": True}}),
    )

    assert ShellyDriver(shelly).get_input_status() is True


# ---------------------------
# set_auth
# ---------------------------
DEVICE_ID = "shellyplus1minig3-abc123"


def test_set_auth_success(mocker, shelly):
    responses = [
        _mock_response(
            mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": False}}
        ),
        _mock_response(mocker, {"id": 1, "result": {}}),
        _mock_response(mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": True}}),
    ]
    mock_post = mocker.patch(
        "actuators.drivers.shelly.requests.post", side_effect=responses
    )

    ShellyDriver(shelly).set_auth("my-password")

    setauth_payload = mock_post.call_args_list[1].kwargs["json"]
    assert setauth_payload["method"] == "Shelly.SetAuth"
    expected_ha1 = hashlib.sha256(
        f"admin:{DEVICE_ID}:my-password".encode()
    ).hexdigest()
    assert setauth_payload["params"] == {
        "user": "admin",
        "realm": DEVICE_ID,
        "ha1": expected_ha1,
    }


def test_set_auth_raises_if_still_disabled_afterwards(mocker, shelly):
    responses = [
        _mock_response(
            mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": False}}
        ),
        _mock_response(mocker, {"id": 1, "result": {}}),
        _mock_response(
            mocker, {"id": 1, "result": {"id": DEVICE_ID, "auth_en": False}}
        ),
    ]
    mocker.patch("actuators.drivers.shelly.requests.post", side_effect=responses)

    with pytest.raises(ShellyError, match="still reports auth disabled"):
        ShellyDriver(shelly).set_auth("my-password")


# ---------------------------
# configure_detached_input
# ---------------------------
def test_configure_detached_input(mocker, shelly):
    mock_post = mocker.patch(
        "actuators.drivers.shelly.requests.post",
        return_value=_mock_response(mocker, {"id": 1, "result": {}}),
    )

    ShellyDriver(shelly).configure_detached_input()

    switch_call, input_call = mock_post.call_args_list

    switch_payload = switch_call.kwargs["json"]
    assert switch_payload["method"] == "Switch.SetConfig"
    assert switch_payload["params"] == {
        "id": 0,
        "config": {"in_mode": "detached", "initial_state": "off"},
    }

    input_payload = input_call.kwargs["json"]
    assert input_payload["method"] == "Input.SetConfig"
    assert input_payload["params"] == {"id": 0, "config": {"type": "switch"}}


# ---------------------------
# _rpc_call error handling
# ---------------------------
def test_rpc_call_timeout(mocker, shelly):
    mocker.patch(
        "actuators.drivers.shelly.requests.post",
        side_effect=requests.exceptions.Timeout("timed out"),
    )

    with pytest.raises(ShellyError, match="timeout"):
        ShellyDriver(shelly).get_switch_status()


def test_rpc_call_401_gives_actionable_message(mocker, shelly):
    resp = mocker.MagicMock()
    resp.status_code = 401
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=resp)
    mocker.patch("actuators.drivers.shelly.requests.post", return_value=resp)

    with pytest.raises(ShellyError, match=r"rejected authentication \(401\)"):
        ShellyDriver(shelly).get_switch_status()


def test_rpc_call_http_error_other_status(mocker, shelly):
    resp = mocker.MagicMock()
    resp.status_code = 500
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError(response=resp)
    mocker.patch("actuators.drivers.shelly.requests.post", return_value=resp)

    with pytest.raises(ShellyError, match="HTTP error"):
        ShellyDriver(shelly).get_switch_status()


def test_rpc_call_connection_error(mocker, shelly):
    mocker.patch(
        "actuators.drivers.shelly.requests.post",
        side_effect=requests.exceptions.ConnectionError("refused"),
    )

    with pytest.raises(ShellyError, match="error on"):
        ShellyDriver(shelly).get_switch_status()


def test_rpc_call_error_in_response_body(mocker, shelly):
    mocker.patch(
        "actuators.drivers.shelly.requests.post",
        return_value=_mock_response(
            mocker,
            {"id": 1, "error": {"code": -103, "message": "Invalid argument"}},
        ),
    )

    with pytest.raises(ShellyError, match="RPC error"):
        ShellyDriver(shelly).get_switch_status()


def test_missing_password_raises_before_any_call(mocker, shelly, settings):
    settings.SHELLY_AUTH_PASSWORD = None
    mock_post = mocker.patch("actuators.drivers.shelly.requests.post")

    with pytest.raises(ShellyError, match="SHELLY_AUTH_PASSWORD"):
        ShellyDriver(shelly).get_switch_status()

    mock_post.assert_not_called()
