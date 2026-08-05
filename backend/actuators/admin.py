from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from actuators.drivers.shelly import ShellyDriver, ShellyError

from .models import Radiator, Shelly


class ShellyAdminForm(forms.ModelForm):
    class Meta:
        model = Shelly
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        ip = cleaned_data.get("ip")
        reference = cleaned_data.get("reference")
        # Provisioning (Shelly.SetAuth) only happens once, at creation — a
        # later edit (e.g. renaming) must not require the device to be online.
        if ip and self.instance.pk is None:
            if Shelly.objects.filter(ip=ip).exists():
                # Let the model's own unique constraint report this error
                # normally — no need to hit the device for a doomed save.
                return cleaned_data
            # Not saved: just carries the two fields ShellyDriver needs
            # (ip, reference) before the real instance exists.
            shelly_preview = Shelly(ip=ip, reference=reference)
            try:
                ShellyDriver(shelly_preview).set_auth(settings.SHELLY_AUTH_PASSWORD)
            except ShellyError as e:
                raise ValidationError(f"Impossible de sécuriser le Shelly : {e}")
        return cleaned_data


@admin.register(Shelly)
class ShellyAdmin(admin.ModelAdmin):
    form = ShellyAdminForm
    list_display = ("name", "reference", "ip")
    list_filter = ("reference",)
    search_fields = ("name", "ip")
    fields = ("name", "reference", "ip")


@admin.register(Radiator)
class RadiatorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "power",
        "control_pin",
        "importance",
        "requested_state",
        "actual_state",
        "last_requested",
    )
    list_filter = ("importance", "requested_state", "actual_state")
    search_fields = ("name",)
    readonly_fields = ("actual_state", "last_requested")

    fields = (
        "name",
        "power",
        "control_pin",
        "importance",
        "requested_state",
        "actual_state",
        "last_requested",
        "error",
    )

    actions = ["set_requested_state_on", "set_requested_state_off"]

    def save_model(self, request, obj, form, change):
        if change:
            original = Radiator.objects.get(pk=obj.pk)
            if original.requested_state != obj.requested_state:
                obj.last_requested = timezone.now()
        else:
            obj.last_requested = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description="Allumer les radiateurs sélectionnés")
    def set_requested_state_on(self, request, queryset):
        updated = queryset.update(
            requested_state=Radiator.RequestedState.ON,
            last_requested=timezone.now(),
        )
        self.message_user(
            request,
            f"{updated} radiateur(s) ont été Allumés.",
            messages.SUCCESS,
        )

    @admin.action(description="Éteindre les radiateurs sélectionnés")
    def set_requested_state_off(self, request, queryset):
        updated = queryset.update(
            requested_state=Radiator.RequestedState.OFF,
            last_requested=timezone.now(),
        )
        self.message_user(
            request,
            f"{updated} radiateur(s) ont été éteins.",
            messages.SUCCESS,
        )
