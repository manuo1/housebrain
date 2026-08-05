"""
Driver to control Shelly Gen2+ devices via their local RPC API (HTTP)
https://shelly-api-docs.shelly.cloud/gen2/General/RPCProtocol
"""

import hashlib
import logging

import requests
from django.conf import settings

from actuators.models import Shelly
from core.constants import UNPLUGGED_MODE, LoggerLabel

logger = logging.getLogger("django")

SHELLY_HTTP_TIMEOUT_SECONDS = 5

# The relay id on single-channel devices (e.g. Shelly 1 Mini Gen3) is
# always 0 — multi-channel devices are not supported by this codebase yet
# (see SUPPORTED_REFERENCES below).
SWITCH_ID = 0

# This driver speaks the generic Shelly Gen2+ RPC protocol, but its switch
# methods hardcode SWITCH_ID = 0, i.e. a single relay. SUPPORTED_REFERENCES
# is an explicit allow-list of references validated as single-relay,
# id=0 devices — NOT a claim that other references use a different
# protocol. A multi-channel device (e.g. a 2-relay Shelly) would need real
# code changes here (switch_id as a parameter) before being added to this
# set; adding a new Shelly.Reference to the model's choices does NOT make
# it usable with this driver until that's done.
SUPPORTED_REFERENCES = {Shelly.Reference.SHELLY_1_MINI_GEN3}


class ShellyError(Exception):
    """Exception for Shelly driver errors"""


def _auth() -> requests.auth.HTTPDigestAuth:
    user = settings.SHELLY_AUTH_USER
    password = settings.SHELLY_AUTH_PASSWORD
    if not user or not password:
        raise ShellyError(
            "SHELLY_AUTH_USER/SHELLY_AUTH_PASSWORD is not set in settings"
        )
    return requests.auth.HTTPDigestAuth(user, password)


class ShellyDriver:
    """Driver to control a single Shelly device's relay over its local RPC API"""

    def __init__(self, shelly: Shelly):
        if shelly.reference not in SUPPORTED_REFERENCES:
            raise ShellyError(
                f"Unsupported Shelly reference {shelly.reference!r}: "
                f"ShellyDriver only supports {sorted(SUPPORTED_REFERENCES)}"
            )
        self.ip = shelly.ip

    def set_switch(self, on: bool, toggle_after: float | None = None):
        """
        Send a switch command to the device.
        Args:
            on: True to turn on, False to turn off
            toggle_after: if set, the device reverts to the opposite state
                by itself after this many seconds — used for momentary/pulse
                commands (e.g. a garage door impulse), no follow-up call needed
        Raises:
            ShellyError: on communication or device error
        """
        if UNPLUGGED_MODE:
            logger.debug(
                f"{LoggerLabel.SHELLYDRIVER} UNPLUGGED mode: "
                f"set_switch({self.ip}, on={on}, toggle_after={toggle_after})"
            )
            return
        params = {"id": SWITCH_ID, "on": on}
        if toggle_after is not None:
            params["toggle_after"] = toggle_after
        self._rpc_call("Switch.Set", params)

    def get_switch_status(self) -> bool:
        """
        Read the current relay state.
        Returns:
            bool: True if ON, False if OFF
        Raises:
            ShellyError: on communication or device error
        """
        if UNPLUGGED_MODE:
            logger.debug(
                f"{LoggerLabel.SHELLYDRIVER} UNPLUGGED mode: "
                f"get_switch_status({self.ip}) -> False"
            )
            return False
        result = self._rpc_call("Switch.GetStatus", {"id": SWITCH_ID})
        return result["output"]

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
        if UNPLUGGED_MODE:
            logger.debug(
                f"{LoggerLabel.SHELLYDRIVER} UNPLUGGED mode: get_device_info({self.ip})"
            )
            return {"id": f"unplugged-{self.ip}", "auth_en": False}
        return self._rpc_call("Shelly.GetDeviceInfo", {})

    def set_auth(self, user: str, password: str):
        """
        Enable digest authentication on the device (Shelly.SetAuth), then
        verify it was actually applied by re-reading the device info.
        Raises:
            ShellyError: on communication/device error, or if the device
                still reports auth as disabled after the call
        """
        if UNPLUGGED_MODE:
            logger.debug(
                f"{LoggerLabel.SHELLYDRIVER} UNPLUGGED mode: set_auth({self.ip})"
            )
            return
        realm = self.get_device_info()["id"]
        ha1 = hashlib.sha256(f"{user}:{realm}:{password}".encode()).hexdigest()
        self._rpc_call("Shelly.SetAuth", {"user": user, "realm": realm, "ha1": ha1})

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
        except requests.exceptions.RequestException as e:
            logger.error(
                f"{LoggerLabel.SHELLYDRIVER} error calling {method} on {self.ip}: {e}"
            )
            raise ShellyError(f"Shelly {self.ip} error on {method}: {e}")

        if "error" in data:
            logger.error(
                f"{LoggerLabel.SHELLYDRIVER} RPC error calling {method} on {self.ip}: {data['error']}"
            )
            raise ShellyError(f"Shelly {self.ip} RPC error on {method}: {data['error']}")

        logger.debug(
            f"{LoggerLabel.SHELLYDRIVER} {method}({self.ip}, {params}) -> {data.get('result')}"
        )
        return data.get("result", {})
