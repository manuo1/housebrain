from django.contrib import admin
from consumption.models import DailyIndexes


@admin.register(DailyIndexes)
class DailyIndexesAdmin(admin.ModelAdmin):
    list_display = ("date",)
    search_fields = ("date",)
