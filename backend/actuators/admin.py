from django.contrib import admin
from django.utils import timezone
from .models import Radiator


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

    readonly_fields = ("actual_state", "last_requested")

    def save_model(self, request, obj, form, change):
        if change:
            original = Radiator.objects.get(pk=obj.pk)
            if original.requested_state != obj.requested_state:
                obj.last_requested = timezone.now()
        else:
            obj.last_requested = timezone.now()

        super().save_model(request, obj, form, change)
