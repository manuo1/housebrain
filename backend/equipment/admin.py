from django.contrib import admin, messages

from device.drivers.base import DeviceDriverError

from .models import GarageDoor, WaterHeater


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


@admin.register(WaterHeater)
class WaterHeaterAdmin(admin.ModelAdmin):
    list_display = ("name", "current_state")
    readonly_fields = ("current_state",)

    actions = ["turn_on_selected", "turn_off_selected"]

    @admin.display(description="État")
    def current_state(self, obj):
        try:
            return obj.get_status()["state"]
        except DeviceDriverError as e:
            return f"Erreur : {e}"

    @admin.action(description="Forcer en marche (HC) les chauffe-eau sélectionnés")
    def turn_on_selected(self, request, queryset):
        self._apply(request, queryset, "turn_on", "forcé(s) en marche")

    @admin.action(description="Forcer à l'arrêt (HP) les chauffe-eau sélectionnés")
    def turn_off_selected(self, request, queryset):
        self._apply(request, queryset, "turn_off", "forcé(s) à l'arrêt")

    def _apply(self, request, queryset, method_name, verb):
        done = 0
        for water_heater in queryset:
            try:
                getattr(water_heater, method_name)()
                done += 1
            except DeviceDriverError as e:
                self.message_user(
                    request,
                    f"{water_heater.name} : échec ({e})",
                    messages.ERROR,
                )
        if done:
            self.message_user(
                request,
                f"{done} chauffe-eau {verb}.",
                messages.SUCCESS,
            )
