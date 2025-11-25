from django.contrib import admin
from django.utils.html import format_html
from heating.models import HeatingPattern, RoomHeatingDayPlan


@admin.register(HeatingPattern)
class HeatingPatternAdmin(admin.ModelAdmin):
    list_display = ["id", "slots_preview", "usage_count", "created_at"]
    readonly_fields = ["slots_hash", "created_at", "usage_count"]
    search_fields = ["slots_hash", "id"]
    list_filter = ["created_at"]

    def slots_preview(self, obj):
        """Display a preview of slots"""
        if not obj.slots:
            return "-"

        max_displayed_slots = 4
        preview_slots = obj.slots[:max_displayed_slots]
        parts = []

        for slot in preview_slots:
            parts.append(f"[{slot['start']}-{slot['end']} {slot['value']}]")

        result = " ".join(parts)

        if len(obj.slots) > max_displayed_slots:
            result += f" +{len(obj.slots) - max_displayed_slots}"

        return result

    slots_preview.short_description = "Créneaux"

    def usage_count(self, obj):
        """Display number of day plans using this pattern"""
        count = obj.day_plans.count()
        return f"{count} plan{'s' if count > 1 else ''}"

    usage_count.short_description = "Utilisations"


@admin.register(RoomHeatingDayPlan)
class RoomHeatingDayPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "room", "date", "heating_pattern", "created_at"]
    list_filter = ["date", "room"]
    search_fields = ["room__name"]
    date_hierarchy = "date"
    autocomplete_fields = ["room", "heating_pattern"]
    readonly_fields = ["created_at", "updated_at", "pattern_details"]

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related("room", "heating_pattern")

    def pattern_details(self, obj):
        """Display detailed pattern information"""
        if not obj.heating_pattern:
            return "-"

        pattern = obj.heating_pattern
        lines = [f"<strong>Pattern {pattern.id}</strong><br>"]

        for slot in pattern.slots:
            lines.append(f"• {slot['start']}-{slot['end']}: {slot['value']}<br>")

        return format_html("".join(lines))

    pattern_details.short_description = "Détails du pattern"
