from django.contrib import admin
from django.utils import formats
from django.utils.html import format_html

from water_heater.models import WaterHeaterDayPlan


@admin.register(WaterHeaterDayPlan)
class WaterHeaterDayPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "water_heater", "weekday", "date", "schedule_pattern"]
    list_filter = ["date", "water_heater", "schedule_pattern"]
    search_fields = ["water_heater__name"]
    date_hierarchy = "date"
    autocomplete_fields = ["water_heater", "schedule_pattern"]
    readonly_fields = ["created_at", "updated_at", "pattern_details"]

    ordering = ["-date"]

    def weekday(self, obj):
        return formats.date_format(obj.date, "l")

    weekday.short_description = "Jour"

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related("water_heater", "schedule_pattern")

    def pattern_details(self, obj):
        """Display detailed pattern information"""
        if not obj.schedule_pattern:
            return "-"
        pattern = obj.schedule_pattern
        lines = [f"<strong>Pattern {pattern.id}</strong><br>"]
        for slot in pattern.slots:
            lines.append(f"• {slot['start']}-{slot['end']}: {slot['value']}<br>")
        return format_html("".join(lines))

    pattern_details.short_description = "Détails du pattern"
