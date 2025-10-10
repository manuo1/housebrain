from django.contrib import admin
from .models import Room


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
