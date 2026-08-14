from types import SimpleNamespace
from unittest.mock import patch

from bluetooth.listener import BluetoothListener


def _advertisement(rssi=-70):
    return SimpleNamespace(rssi=rssi, service_data={"0000fcd2": b"payload"})


def _device(address="38:1F:8D:65:E9:1C", name="TH05-65E91C"):
    return SimpleNamespace(address=address, name=name)


class TestDetectionCallback:
    def setup_method(self):
        self.listener = BluetoothListener()

    def test_valid_measurement_with_temperature_is_buffered(self):
        device = _device()
        advertisement_data = _advertisement()

        with (
            patch(
                "bluetooth.listener.decode_bthome_payload",
                return_value={"battery": 60, "temperature": 20.5},
            ),
            patch("bluetooth.listener.timezone.now") as mock_now,
        ):
            mock_now.return_value.isoformat.return_value = "2026-01-01T00:00:00"
            self.listener.detection_callback(device, advertisement_data)

        assert self.listener.buffered_sensors == {
            device.address: {
                "mac_address": device.address,
                "name": device.name,
                "rssi": advertisement_data.rssi,
                "measurements": {
                    "battery": 60,
                    "temperature": 20.5,
                    "dt": "2026-01-01T00:00:00",
                },
            }
        }

    def test_undecodable_payload_is_ignored(self):
        device = _device()
        advertisement_data = _advertisement()

        with patch(
            "bluetooth.listener.decode_bthome_payload", return_value=None
        ):
            self.listener.detection_callback(device, advertisement_data)

        assert self.listener.buffered_sensors == {}

    def test_measurements_without_temperature_are_ignored(self):
        """Un payload BTHome décodé mais sans mesure de température (ex: un
        capteur qui n'envoie que la batterie) est ignoré."""
        device = _device()
        advertisement_data = _advertisement()

        with patch(
            "bluetooth.listener.decode_bthome_payload",
            return_value={"battery": 60},
        ):
            self.listener.detection_callback(device, advertisement_data)

        assert self.listener.buffered_sensors == {}

    def test_zero_temperature_is_still_buffered(self):
        """0.00°C est une mesure valide, pas une absence de mesure."""
        device = _device()
        advertisement_data = _advertisement()

        with (
            patch(
                "bluetooth.listener.decode_bthome_payload",
                return_value={"temperature": 0.0},
            ),
            patch(
                "bluetooth.listener.timezone.now",
            ) as mock_now,
        ):
            mock_now.return_value.isoformat.return_value = "2026-01-01T00:00:00"
            self.listener.detection_callback(device, advertisement_data)

        assert self.listener.buffered_sensors == {
            device.address: {
                "mac_address": device.address,
                "name": device.name,
                "rssi": advertisement_data.rssi,
                "measurements": {
                    "temperature": 0.0,
                    "dt": "2026-01-01T00:00:00",
                },
            }
        }

    def test_device_without_name_falls_back_to_unknown(self):
        device = _device(name=None)
        advertisement_data = _advertisement()

        with (
            patch(
                "bluetooth.listener.decode_bthome_payload",
                return_value={"temperature": 20.5},
            ),
            patch("bluetooth.listener.timezone.now"),
        ):
            self.listener.detection_callback(device, advertisement_data)

        assert self.listener.buffered_sensors[device.address]["name"] == "Unknown"


class TestUpdateCacheWithBufferedData:
    def setup_method(self):
        self.listener = BluetoothListener()

    def test_pings_watchdog(self):
        with (
            patch("bluetooth.listener.get_sensors_data_in_cache", return_value={}),
            patch("bluetooth.listener.notify_watchdog") as mock_notify,
            patch("bluetooth.listener.cache.set"),
        ):
            self.listener.update_cache_with_buffered_data()

        mock_notify.assert_called_once()

    def test_new_sensor_has_no_previous_measurements(self):
        self.listener.buffered_sensors = {
            "AA:BB": {
                "mac_address": "AA:BB",
                "name": "Sensor",
                "rssi": -70,
                "measurements": {"temperature": 20.5, "dt": "2026-01-01T00:00:00"},
            }
        }

        with (
            patch("bluetooth.listener.get_sensors_data_in_cache", return_value={}),
            patch("bluetooth.listener.notify_watchdog"),
            patch("bluetooth.listener.cache.set") as mock_cache_set,
        ):
            self.listener.update_cache_with_buffered_data()

        saved = mock_cache_set.call_args.args[1]
        assert saved["AA:BB"]["previous_measurements"] == {}

    def test_previously_seen_sensor_keeps_its_last_measurements_as_previous(self):
        self.listener.buffered_sensors = {
            "AA:BB": {
                "mac_address": "AA:BB",
                "name": "Sensor",
                "rssi": -70,
                "measurements": {"temperature": 21.0, "dt": "2026-01-01T00:01:00"},
            }
        }
        existing_cache = {
            "AA:BB": {
                "mac_address": "AA:BB",
                "name": "Sensor",
                "rssi": -75,
                "measurements": {"temperature": 20.5, "dt": "2026-01-01T00:00:00"},
                "previous_measurements": {},
            }
        }

        with (
            patch(
                "bluetooth.listener.get_sensors_data_in_cache",
                return_value=existing_cache,
            ),
            patch("bluetooth.listener.notify_watchdog"),
            patch("bluetooth.listener.cache.set") as mock_cache_set,
        ):
            self.listener.update_cache_with_buffered_data()

        saved = mock_cache_set.call_args.args[1]
        assert saved["AA:BB"]["previous_measurements"] == {
            "temperature": 20.5,
            "dt": "2026-01-01T00:00:00",
        }
        assert saved["AA:BB"]["measurements"] == {
            "temperature": 21.0,
            "dt": "2026-01-01T00:01:00",
        }

    def test_sensors_not_seen_this_cycle_are_kept_untouched_in_cache(self):
        """Un capteur absent du buffer de ce cycle (hors de portée, batterie
        morte...) doit rester dans le cache tel qu'il était, pas disparaître."""
        self.listener.buffered_sensors = {}
        existing_cache = {
            "AA:BB": {"mac_address": "AA:BB", "measurements": {"temperature": 19.0}}
        }

        with (
            patch(
                "bluetooth.listener.get_sensors_data_in_cache",
                return_value=existing_cache,
            ),
            patch("bluetooth.listener.notify_watchdog"),
            patch("bluetooth.listener.cache.set") as mock_cache_set,
        ):
            self.listener.update_cache_with_buffered_data()

        saved = mock_cache_set.call_args.args[1]
        assert saved == existing_cache
