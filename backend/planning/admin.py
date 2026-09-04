from django.contrib import admin

from .models import SchedulePattern


@admin.register(SchedulePattern)
class SchedulePatternAdmin(admin.ModelAdmin):
    list_display = ["id", "slots_preview", "usage_count_display", "created_at"]
    readonly_fields = ["slots_hash", "created_at", "usage_count_display"]
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

    def usage_count_display(self, obj):
        """Display number of day plans (any type) using this pattern"""
        count = obj.usage_count()
        return f"{count} plan{'s' if count > 1 else ''}"

    usage_count_display.short_description = "Utilisations"
