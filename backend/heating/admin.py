from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.db import IntegrityError
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


class DuplicateToDateActionForm(ActionForm):
    new_date = forms.DateField(
        label="Duplicate to date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@admin.register(RoomHeatingDayPlan)
class RoomHeatingDayPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "room", "date", "heating_pattern"]
    list_filter = ["date", "room", "heating_pattern"]
    search_fields = ["room__name"]
    date_hierarchy = "date"
    autocomplete_fields = ["room", "heating_pattern"]
    readonly_fields = ["created_at", "updated_at", "pattern_details"]
    actions = ["duplicate_to_date"]

    action_form = DuplicateToDateActionForm

    ordering = ["-date"]

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

    def duplicate_to_date(self, request, queryset):
        """Allow the user to duplicate a RoomHeatingDay plan to another date"""

        form = self.action_form(request.POST)
        form.fields["action"].choices = self.get_action_choices(request)

        if not form.is_valid():
            self.message_user(request, "Invalid or missing date.", level="error")
            return

        new_date = form.cleaned_data["new_date"]

        created = 0
        skipped = 0

        for plan in queryset:
            try:
                RoomHeatingDayPlan.objects.create(
                    room=plan.room,
                    date=new_date,
                    heating_pattern=plan.heating_pattern,
                )
                created += 1
            except IntegrityError:
                skipped += 1

        if created:
            self.message_user(request, f"{created} plan(s) duplicated to {new_date}.")

        if skipped:
            self.message_user(
                request,
                f"{skipped} plan duplication(s) skipped: a plan already exists for this date.",
                level="warning",
            )
