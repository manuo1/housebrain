from django.contrib import admin

from heating.services.heating_synchronization import (
    queue_radiators_to_turn_on,
    resolve_radiators_to_update,
    turn_off_radiators_and_apply_to_hardware,
)
from rooms.models import Room


def synchronize_radiators() -> None:
    radiators_to_update = resolve_radiators_to_update()
    turn_off_radiators_and_apply_to_hardware(radiators_to_update)
    queue_radiators_to_turn_on(radiators_to_update)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "heating_control_mode",
        "temperature_setpoint",
        "requested_heating_state",
    )
    list_filter = ("heating_control_mode", "requested_heating_state")
    search_fields = ("name",)
    ordering = ("name",)

    actions = ["set_heating_on", "set_heating_off"]

    fieldsets = (
        (
            "Informations générales",
            {
                "fields": ("name",),
            },
        ),
        (
            "Association de matériel",
            {
                "fields": ("temperature_sensor", "radiator"),
                "description": "Capteur et radiateur associés à cette pièce.",
            },
        ),
        (
            "Définition des consignes",
            {
                "fields": (
                    "heating_control_mode",
                    "temperature_setpoint",
                    "requested_heating_state",
                ),
                "description": "Paramètres de pilotage et consignes pour le chauffage.",
            },
        ),
    )

    @admin.action(
        description="État du chauffage sur Allumé pour les pièces sélectionnées"
    )
    def set_heating_on(self, request, queryset):
        updated = queryset.update(requested_heating_state=Room.RequestedHeatingState.ON)
        self.message_user(
            request,
            f"{updated} pièce(s) mise(s) sur ON avec succès.",
        )
        synchronize_radiators()

    @admin.action(
        description="État du chauffage sur Éteint pour les pièces sélectionnées"
    )
    def set_heating_off(self, request, queryset):
        updated = queryset.update(
            requested_heating_state=Room.RequestedHeatingState.OFF
        )
        self.message_user(
            request,
            f"{updated} pièce(s) mise(s) sur OFF avec succès.",
        )
        synchronize_radiators()
