from django.contrib import admin
from monitoring.models import SystemLog


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ["logged_at", "service", "level", "message_preview", "created_at"]
    list_filter = ["service", "level", "logged_at", "created_at"]
    search_fields = ["message"]
    readonly_fields = ["service", "level", "message", "logged_at", "created_at"]
    date_hierarchy = "logged_at"
    ordering = ["-logged_at"]

    def message_preview(self, obj):
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message

    message_preview.short_description = "Message"
