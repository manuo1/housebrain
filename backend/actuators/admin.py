from django.contrib import admin, messages
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
