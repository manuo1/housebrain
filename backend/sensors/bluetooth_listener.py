import logging
import asyncio
from core.utils.systemd_utils import notify_watchdog
from bleak import BleakScanner
from django.core.cache import caches
from django.utils import timezone
from sensors.services.bthome import decode_bthome_payload

cache = caches["default"]
logger = logging.getLogger("django")


class BluetoothListener:
    def __init__(self):
        self.sensors = {}
        cache.set("sensors_data", {"created": timezone.now(), "last_saved_at": None})

    async def start_scanner(self):
        """Starts the Bluetooth listener process."""
        try:
            logger.info("BluetoothListener: Listening for BTHome sensors...")

            scanner = BleakScanner(detection_callback=self.detection_callback)
            while True:
                await scanner.start()
                await asyncio.sleep(10)  # Scan duration
                await scanner.stop()
                await asyncio.sleep(30)  # Pause between scans
        except Exception as e:
            logger.error(f"BluetoothListener: Error in listener - {e}")

    def detection_callback(self, device, advertisement_data):
        for _, payload in advertisement_data.service_data.items():
            measurements = decode_bthome_payload(payload)
            if measurements:
                self.sensors[device.address] = {
                    "mac_address": device.address,
                    "name": device.name or "Unknown",
                    "rssi": advertisement_data.rssi,
                    "last_seen": timezone.now(),
                    **measurements,
                }

                cache.set("sensors_data", self.sensors)
                notify_watchdog()
                logger.info(f"BluetoothListener: Updated sensor {device.address}")

    def start(self):
        """Synchronous method to start the Bluetooth listener."""
        asyncio.run(self.start_scanner())
