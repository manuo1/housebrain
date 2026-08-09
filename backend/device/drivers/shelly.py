"""
Driver to control Shelly Gen2+ devices via their local RPC API (HTTP)
https://shelly-api-docs.shelly.cloud/gen2/General/RPCProtocol

This is the device-app-level replacement for the old
actuators/drivers/shelly.py (kept there for now, still used by the
existing PulseSwitch/equipment code — see [[housebrain-device]] notes on
the migration plan; nothing in this file is wired to anything yet).
"""

import hashlib
import logging

import requests
from django.conf import settings

from core.constants import LoggerLabel
from device.catalog import Shelly1MiniGen3
from device.drivers.base import DeviceDriver, DeviceDriverError
from device.models import IPDevice

logger = logging.getLogger("django")

SHELLY_HTTP_TIMEOUT_SECONDS = 5

# This driver speaks the generic Shelly Gen2+ RPC protocol, but hardcodes
# id=0 for both the relay and the SW input — i.e. a single-channel device.
# Shelly1MiniGen3 is the only DeviceModelSpec wired to this driver today;
# a multi-channel Shelly would need real code changes here (an id per
# io_key) before it could reuse this driver as-is.
_IO_TO_SWITCH_ID = {"relay": 0}
_IO_TO_INPUT_ID = {"sw": 0}

# Shelly.SetAuth / digest auth only ever accept this username — fixed by
# the firmware, not configurable (confirmed by device error -103 "Only
# user 'admin' is supported!" when anything else was tried).
SHELLY_AUTH_USER = "admin"


class ShellyError(DeviceDriverError):
    """Exception for Shelly driver errors"""


def _auth() -> requests.auth.HTTPDigestAuth:
    password = settings.SHELLY_AUTH_PASSWORD
    if not password:
        raise ShellyError("SHELLY_AUTH_PASSWORD is not set in settings")
    return requests.auth.HTTPDigestAuth(SHELLY_AUTH_USER, password)


class ShellyDriver(DeviceDriver):
    """Driver to control a single Shelly device's relay/input over its local RPC API"""

    def __init__(self, device):
        """
        device: any Device instance (base class) for a Shelly1MiniGen3 —
        resolved here to the concrete IPDevice to reach its `ip`, so
        callers (e.g. DeviceIO.get_driver()) never need to know Shelly is
        IP-based.
        """
        if device.reference != Shelly1MiniGen3.reference:
            raise ShellyError(
                f"Unsupported device reference {device.reference!r}: "
                f"ShellyDriver only supports {Shelly1MiniGen3.reference!r}"
            )
        ip_device = device if isinstance(device, IPDevice) else IPDevice.objects.get(pk=device.pk)
        self.ip = ip_device.ip

    def read_io_state(self, io_key: str) -> bool:
        if io_key in _IO_TO_SWITCH_ID:
            result = self._rpc_call(
                "Switch.GetStatus", {"id": _IO_TO_SWITCH_ID[io_key]}
            )
            return result["output"]
        if io_key in _IO_TO_INPUT_ID:
            # Meaningful only if something is actually wired to SW (e.g. a
            # reed switch) — works regardless of sensor mode, since
            # Input.GetStatus and Switch.GetStatus are independent
            # components with their own state.
            result = self._rpc_call("Input.GetStatus", {"id": _IO_TO_INPUT_ID[io_key]})
            return result["state"]
        raise ShellyError(f"Unknown io_key {io_key!r} for {self.ip}")

    def set_io_output(
        self, io_key: str, on: bool, pulse_seconds: float | None = None
    ) -> None:
        if io_key not in _IO_TO_SWITCH_ID:
            raise ShellyError(f"IO {io_key!r} is not an output IO on {self.ip}")
        params = {"id": _IO_TO_SWITCH_ID[io_key], "on": on}
        if pulse_seconds is not None:
            params["toggle_after"] = pulse_seconds
        self._rpc_call("Switch.Set", params)

    def set_sensor_mode(self, io_key: str, enabled: bool) -> None:
        if io_key not in _IO_TO_INPUT_ID:
            raise ShellyError(
                f"IO {io_key!r} does not support sensor mode on {self.ip}"
            )
        if enabled:
            self._set_sw_terminal_as_sensor()
        else:
            self._set_sw_terminal_as_switch()

    def _set_sw_terminal_as_sensor(self):
        """
        Configure the SW terminal as a readable input, detached from the
        relay (in_mode="detached", so wiring something to SW no longer
        triggers the output) and set its type to "switch" (a maintained
        contact, e.g. a reed switch — as opposed to "button", a momentary
        contact).

        IMPORTANT: run this BEFORE wiring anything to SW. Wiring a contact
        to SW while still in the default (relay switch) mode can trigger
        the relay on connection — an unintended door pulse.
        Raises:
            ShellyError: on communication or device error
        """
        # initial_state must be changed together with in_mode: the default
        # "match_input" is only valid while in_mode="follow" (device error
        # -103 "invalid combination" otherwise). "off" is the right resting
        # state here: after a reboot/power loss, the relay should stay off,
        # not attempt to restore whatever transient state it was in.
        self._rpc_call(
            "Switch.SetConfig",
            {
                "id": _IO_TO_SWITCH_ID["relay"],
                "config": {"in_mode": "detached", "initial_state": "off"},
            },
        )
        self._rpc_call(
            "Input.SetConfig",
            {"id": _IO_TO_INPUT_ID["sw"], "config": {"type": "switch"}},
        )

    def _set_sw_terminal_as_switch(self):
        """
        Configure the SW terminal as the relay's physical switch (factory
        behavior, in_mode="follow"): wiring/toggling SW directly drives the
        relay output, either locally or remotely. Reverts
        _set_sw_terminal_as_sensor().
        Raises:
            ShellyError: on communication or device error
        """
        # See _set_sw_terminal_as_sensor(): in_mode="follow" requires
        # initial_state="match_input" (the factory default combination).
        self._rpc_call(
            "Switch.SetConfig",
            {
                "id": _IO_TO_SWITCH_ID["relay"],
                "config": {"in_mode": "follow", "initial_state": "match_input"},
            },
        )
        self._rpc_call(
            "Input.SetConfig",
            {"id": _IO_TO_INPUT_ID["sw"], "config": {"type": "switch"}},
        )

    def get_device_info(self) -> dict:
        """
        Read the device's own identity/auth status. Does not require auth
        (Shelly.GetDeviceInfo is a public RPC method), so this also works
        against a freshly-provisioned device that has no auth configured yet.
        Returns:
            dict: notably "id" (used as the realm for digest auth) and
                "auth_en" (bool, whether auth is currently enabled)
        Raises:
            ShellyError: on communication or device error
        """
        return self._rpc_call("Shelly.GetDeviceInfo", {})

    def set_auth(self, password: str):
        """
        Enable digest authentication on the device (Shelly.SetAuth), then
        verify it was actually applied by re-reading the device info.
        Raises:
            ShellyError: on communication/device error, or if the device
                still reports auth as disabled after the call
        """
        realm = self.get_device_info()["id"]
        ha1 = hashlib.sha256(
            f"{SHELLY_AUTH_USER}:{realm}:{password}".encode()
        ).hexdigest()
        self._rpc_call(
            "Shelly.SetAuth", {"user": SHELLY_AUTH_USER, "realm": realm, "ha1": ha1}
        )

        if not self.get_device_info()["auth_en"]:
            raise ShellyError(
                f"Shelly {self.ip} still reports auth disabled after Shelly.SetAuth"
            )

    def _rpc_call(self, method: str, params: dict) -> dict:
        """
        Call a Shelly RPC method over HTTP and return its "result" payload.
        Raises:
            ShellyError: on timeout, network error, HTTP error status, or an
                {"error": ...} RPC response
        """
        payload = {"id": 1, "method": method, "params": params}
        try:
            response = requests.post(
                f"http://{self.ip}/rpc",
                json=payload,
                auth=_auth(),
                timeout=SHELLY_HTTP_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout as e:
            logger.error(
                f"{LoggerLabel.SHELLYDRIVER} timeout calling {method} on {self.ip}: {e}"
            )
            raise ShellyError(f"Shelly {self.ip} timeout on {method}: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                message = (
                    f"Shelly {self.ip} rejected authentication (401) on {method}: "
                    "a different password is already configured on this device. "
                    "Check SHELLY_AUTH_PASSWORD, or factory-reset the Shelly "
                    "(hold its physical button 10s) to start over."
                )
            else:
                message = f"Shelly {self.ip} HTTP error on {method}: {e}"
            logger.error(f"{LoggerLabel.SHELLYDRIVER} {message}")
            raise ShellyError(message)
        except requests.exceptions.RequestException as e:
            logger.error(
                f"{LoggerLabel.SHELLYDRIVER} error calling {method} on {self.ip}: {e}"
            )
            raise ShellyError(f"Shelly {self.ip} error on {method}: {e}")

        if "error" in data:
            logger.error(
                f"{LoggerLabel.SHELLYDRIVER} RPC error calling {method} on {self.ip}: {data['error']}"
            )
            raise ShellyError(
                f"Shelly {self.ip} RPC error on {method}: {data['error']}"
            )

        logger.debug(
            f"{LoggerLabel.SHELLYDRIVER} {method}({self.ip}, {params}) -> {data.get('result')}"
        )
        return data.get("result", {})
