from django.contrib import admin
from heating.models import HeatingPattern, RoomHeatingDayPlan


@admin.register(HeatingPattern)
class HeatingPatternAdmin(admin.ModelAdmin):
    list_display = ["id", "slots_preview", "slots_hash", "created_at"]
    readonly_fields = ["slots_hash", "created_at"]
    search_fields = ["slots_hash"]

    def slots_preview(self, obj):
        """Display a preview of slots"""
        if not obj.slots:
            return "-"
        count = len(obj.slots)
        return f"{count} créneau{'x' if count > 1 else ''}"

    slots_preview.short_description = "Créneaux"


@admin.register(RoomHeatingDayPlan)
class RoomHeatingDayPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "room", "date", "heating_pattern", "created_at"]
    list_filter = ["date", "room"]
    search_fields = ["room__name"]
    date_hierarchy = "date"
    autocomplete_fields = ["room", "heating_pattern"]
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related("room", "heating_pattern")
