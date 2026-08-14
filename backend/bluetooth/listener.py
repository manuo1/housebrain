import asyncio
import logging

from bleak import BleakScanner
from bleak.exc import BleakError
from django.core.cache import caches
from django.utils import timezone

from bluetooth.services.bthome import decode_bthome_payload
from bluetooth.utils.cache_bluetooth_data import get_sensors_data_in_cache
from core.constants import LoggerLabel
from core.utils.systemd_utils import notify_watchdog

cache = caches["default"]
logger = logging.getLogger("django")


SCAN_DURATION = 30
PAUSE_DURATION = 30


class BluetoothListener:
    def __init__(self):
        cache.set("bluetooth_data", {}, timeout=None)
        self.buffered_sensors = {}

    async def start_scanner(self):
        """Starts the Bluetooth listener process.

        Only known, recoverable Bluetooth adapter errors (BleakError) are
        caught here and retried in place. Any other (unexpected) exception
        is intentionally left to propagate: it kills the process and lets
        systemd's Restart=always take over, instead of silently looping on
        a possibly broken state (same choice as TeleinfoListener).
        """
        logger.info(
            f"{LoggerLabel.BLUETOOTHLISTENER} Listening for BTHome sensors..."
        )

        while True:
            self.buffered_sensors.clear()
            scanner = BleakScanner(detection_callback=self.detection_callback)

            try:
                await scanner.start()
                await asyncio.sleep(SCAN_DURATION)
                await scanner.stop()
            except BleakError as e:
                logger.error(
                    f"{LoggerLabel.BLUETOOTHLISTENER} Bluetooth adapter error - {e}"
                )
                notify_watchdog()
                await asyncio.sleep(PAUSE_DURATION)
                continue

            self.update_cache_with_buffered_data()
            await asyncio.sleep(PAUSE_DURATION)

    def detection_callback(self, device, advertisement_data):
        """Called every time a BLE packet is received."""
        for _, payload in advertisement_data.service_data.items():
            measurements = decode_bthome_payload(payload)
            if not measurements or "temperature" not in measurements:
                continue

            self.buffered_sensors[device.address] = {
                "mac_address": device.address,
                "name": device.name or "Unknown",
                "rssi": advertisement_data.rssi,
                "measurements": {**measurements, "dt": timezone.now().isoformat()},
            }

    def update_cache_with_buffered_data(self):
        """Update the cache only once per scan cycle."""
        notify_watchdog()
        sensors_data = get_sensors_data_in_cache()

        for mac, data in self.buffered_sensors.items():
            previous = sensors_data.get(mac, {})
            sensors_data[mac] = {
                **data,
                "previous_measurements": previous.get("measurements", {}),
            }

        cache.set("bluetooth_data", sensors_data, timeout=None)

    def start(self):
        """Synchronous method to start the Bluetooth listener."""
        asyncio.run(self.start_scanner())
