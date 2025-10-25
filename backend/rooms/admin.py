from django.contrib import admin
from heating.services.heating_synchronization import HeatingSyncService
from rooms.models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "heating_control_mode",
        "current_setpoint",
        "current_on_off_state",
    )
    list_filter = ("heating_control_mode", "current_on_off_state")
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
                    "current_setpoint",
                    "current_on_off_state",
                ),
                "description": "Paramètres de pilotage et consignes pour le chauffage.",
            },
        ),
    )

    @admin.action(
        description="État du chauffage sur Allumé pour les pièces sélectionnées"
    )
    def set_heating_on(self, request, queryset):
        updated = queryset.update(current_on_off_state=Room.CurrentHeatingState.ON)
        self.message_user(
            request,
            f"{updated} pièce(s) mise(s) sur ON avec succès.",
        )
        HeatingSyncService.synchronize_rooms_with_on_off_heating_control()

    @admin.action(
        description="État du chauffage sur Éteint pour les pièces sélectionnées"
    )
    def set_heating_off(self, request, queryset):
        updated = queryset.update(current_on_off_state=Room.CurrentHeatingState.OFF)
        self.message_user(
            request,
            f"{updated} pièce(s) mise(s) sur OFF avec succès.",
        )
        HeatingSyncService.synchronize_rooms_with_on_off_heating_control()
