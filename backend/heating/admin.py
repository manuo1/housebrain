from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.db import IntegrityError
from django.utils import formats
from django.utils.html import format_html

from heating.models import RoomHeatingDayPlan


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
    list_display = ["id", "room", "weekday", "date", "heating_pattern"]
    list_filter = ["date", "room", "heating_pattern"]
    search_fields = ["room__name"]
    date_hierarchy = "date"
    autocomplete_fields = ["room", "heating_pattern"]
    readonly_fields = ["created_at", "updated_at", "pattern_details"]
    actions = ["duplicate_to_date"]

    action_form = DuplicateToDateActionForm

    ordering = ["-date"]

    def weekday(self, obj):
        return formats.date_format(obj.date, "l")

    weekday.short_description = "Jour"

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
