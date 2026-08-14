from django import forms
from django.contrib import admin

from bluetooth.utils.cache_bluetooth_data import get_sensors_data_in_cache
from device.drivers.base import DeviceDriverError

from .models import DoorContactSensor, TemperatureSensor


class TemperatureSensorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sensors_data = get_sensors_data_in_cache()
        macs_in_cache = sorted(sensors_data.keys())

        macs_already_in_db = TemperatureSensor.objects.exclude(
            pk=self.instance.pk if self.instance.pk else None
        ).values_list("mac_address", flat=True)

        macs_for_admin = [mac for mac in macs_in_cache if mac not in macs_already_in_db]

        choices = [("", "--- Choisir un capteur ---")]
        for mac in macs_for_admin:
            sensor = sensors_data[mac]
            name = sensor.get("name", "Unknown")
            rssi = sensor.get("rssi", "?")
            label = f"{mac} ({name}, RSSI: {rssi})"
            choices.append((mac, label))

        self.fields["mac_address"].widget = forms.Select(choices=choices)

    class Meta:
        model = TemperatureSensor
        fields = "__all__"


@admin.register(TemperatureSensor)
class TemperatureSensorAdmin(admin.ModelAdmin):
    form = TemperatureSensorForm
    list_display = ["name", "mac_address"]


@admin.register(DoorContactSensor)
class DoorContactSensorAdmin(admin.ModelAdmin):
    list_display = ("name", "current_state")
    readonly_fields = ("current_state",)

    @admin.display(description="État")
    def current_state(self, obj):
        try:
            return obj.get_readable_state()
        except DeviceDriverError as e:
            return f"Erreur : {e}"
