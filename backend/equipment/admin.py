from django.contrib import admin, messages

from equipment.models import PulseSwitch
from equipment.services.pulse_switch import PulseSwitchError, PulseSwitchService


@admin.register(PulseSwitch)
class PulseSwitchAdmin(admin.ModelAdmin):
    list_display = ("name", "shelly", "status", "last_triggered_at")
    list_filter = ("status",)
    search_fields = ("name",)
    readonly_fields = ("status", "last_triggered_at")

    fields = ("name", "shelly", "status", "last_triggered_at")

    actions = ["trigger_selected"]

    @admin.action(description="Déclencher l'impulsion")
    def trigger_selected(self, request, queryset):
        for pulse_switch in queryset:
            try:
                PulseSwitchService.trigger(
                    pulse_switch.pk, triggered_by_username=request.user.username
                )
            except PulseSwitchError as e:
                self.message_user(
                    request,
                    f"{pulse_switch.name} : {e}",
                    messages.ERROR,
                )
            else:
                self.message_user(
                    request,
                    f"{pulse_switch.name} déclenché.",
                    messages.SUCCESS,
                )
