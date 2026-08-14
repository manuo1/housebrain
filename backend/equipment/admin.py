from django.contrib import admin, messages

from device.drivers.base import DeviceDriverError

from .models import GarageDoor


@admin.register(GarageDoor)
class GarageDoorAdmin(admin.ModelAdmin):
    list_display = ("name", "current_state")
    readonly_fields = ("current_state",)

    actions = ["trigger_selected"]

    @admin.display(description="État")
    def current_state(self, obj):
        try:
            return obj.get_status()["state"]
        except DeviceDriverError as e:
            return f"Erreur : {e}"

    @admin.action(description="Déclencher (trigger) les portes sélectionnées")
    def trigger_selected(self, request, queryset):
        triggered = 0
        for door in queryset:
            try:
                door.trigger()
                triggered += 1
            except DeviceDriverError as e:
                self.message_user(
                    request,
                    f"{door.name} : échec du déclenchement ({e})",
                    messages.ERROR,
                )
        if triggered:
            self.message_user(
                request,
                f"{triggered} porte(s) déclenchée(s).",
                messages.SUCCESS,
            )
