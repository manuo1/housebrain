from django.contrib import admin
from consumption.models import DailyConsumption


@admin.register(DailyConsumption)
class DailyConsumptionAdmin(admin.ModelAdmin):
    list_display = ("date",)
    search_fields = ("date",)
