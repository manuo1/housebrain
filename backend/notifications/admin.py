from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "level", "event_code", "status", "triggered_by_username")
    list_filter = ("level", "status")
    search_fields = ("event_code", "message", "triggered_by_username")
    readonly_fields = (
        "event_code",
        "level",
        "message",
        "triggered_by_username",
        "status",
        "created_at",
        "sent_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
