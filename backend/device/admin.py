from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError

from device.catalog import IO_TYPE_ALLOWED_MODES, IOMode, Shelly1MiniGen3
from device.drivers.shelly import ShellyDriver, ShellyError
from device.models import DeviceIO, IPDevice
from device.services.device_io import DeviceIOError, DeviceIOService


class IPDeviceAdminForm(forms.ModelForm):
    """
    Secures a newly created Shelly (driver-level auth setup) before it's
    saved — mirrors the previous actuators.ShellyAdminForm, the pattern
    this replaces. Shelly-specific for now: it's the only supported
    reference, so no need yet for a generic "does this driver support
    onboarding" indirection.
    """

    class Meta:
        model = IPDevice
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        ip = cleaned_data.get("ip")
        reference = cleaned_data.get("reference")
        # Provisioning (driver-level auth setup) only happens once, at
        # creation — a later edit (e.g. renaming) must not require the
        # device to be online.
        if ip and reference == Shelly1MiniGen3.reference and self.instance.pk is None:
            if IPDevice.objects.filter(ip=ip).exists():
                # Let the model's own unique constraint report this error
                # normally — no need to hit the device for a doomed save.
                return cleaned_data
            # Not saved: just carries the two fields ShellyDriver needs
            # (ip, reference) before the real instance exists.
            device_preview = IPDevice(reference=reference, ip=ip)
            try:
                ShellyDriver(device_preview).set_auth(settings.SHELLY_AUTH_PASSWORD)
            except ShellyError as e:
                raise ValidationError(f"Impossible de sécuriser le device : {e}")
        return cleaned_data


class DeviceIOForm(forms.ModelForm):
    """
    Restricts the `mode` field's choices to whatever this specific IO's
    IOType allows (see device.catalog.IO_TYPE_ALLOWED_MODES) — e.g. a
    relay IO only ever shows/accepts RELAY_ON_OFF, a togglable IO only
    shows SENSOR_TRUE_FALSE / NOT_USED_IN_APP.

    Also routes any actual mode change through DeviceIOService.set_io_mode()
    instead of a plain model save — a bare save() would silently skip the
    driver call and the RelayOnOff/SensorTrueFalse bookkeeping.
    """

    class Meta:
        model = DeviceIO
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_modes = self._get_allowed_modes()
        if allowed_modes is None:
            # No provisioned IO yet to look up (shouldn't happen in
            # practice: rows are only ever shown once provisioned, and
            # manual add is disabled — see DeviceIOInline.has_add_permission).
            return
        allowed_values = {mode.value for mode in allowed_modes}
        self.fields["mode"].choices = [
            choice for choice in self.fields["mode"].choices if choice[0] in allowed_values
        ]
        if len(allowed_modes) == 1:
            # Only one legal value (a fixed-role IO, e.g. a relay): show it
            # but don't let it be edited — Django keeps the initial value
            # for a disabled field regardless of what's posted, and
            # excludes it from changed_data, so save() below never routes
            # it through set_io_mode().
            self.fields["mode"].disabled = True

    def _get_allowed_modes(self):
        device = self.instance.device if self.instance.device_id else None
        if device is None or not self.instance.key:
            return None
        try:
            io_spec = device.get_model_spec().get_io_spec(self.instance.key)
        except ValueError:
            return None
        return IO_TYPE_ALLOWED_MODES[io_spec.type]

    def clean(self):
        cleaned_data = super().clean()
        # Runs before Django populates self.instance from cleaned_data (see
        # ModelForm._post_clean()), so self.instance.mode here is still the
        # DB value — comparing it to cleaned_data catches the real change.
        new_mode = cleaned_data.get("mode")
        if new_mode and self.instance.pk and new_mode != self.instance.mode:
            try:
                DeviceIOService.set_io_mode(self.instance.pk, IOMode(new_mode))
            except DeviceIOError as e:
                raise ValidationError(f"Impossible de changer le mode : {e}")
        return cleaned_data


class DeviceIOInline(admin.TabularInline):
    model = DeviceIO
    form = DeviceIOForm
    extra = 0
    can_delete = False
    fields = ("key", "name", "mode")
    readonly_fields = ("key", "name")

    def has_add_permission(self, request, obj):
        # DeviceIO rows are provisioned automatically (see
        # DeviceIOService.provision_device(), called from
        # IPDeviceAdmin.save_model() below) — never added by hand.
        return False


@admin.register(IPDevice)
class IPDeviceAdmin(admin.ModelAdmin):
    form = IPDeviceAdminForm
    list_display = ("name", "reference", "ip")
    list_filter = ("reference",)
    search_fields = ("name", "ip")
    inlines = [DeviceIOInline]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new:
            DeviceIOService.provision_device(obj)

    def has_delete_permission(self, request, obj=None):
        # Blocks deletion when an orphan business-layer object (e.g. a
        # SingleButtonMotor never assembled into a GarageDoor) would be
        # silently cascade-deleted - see DeviceIOService.is_device_deletable().
        if obj is not None and not DeviceIOService.is_device_deletable(obj):
            return False
        return super().has_delete_permission(request, obj)
