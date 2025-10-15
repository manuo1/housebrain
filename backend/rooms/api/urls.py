from django.urls import path
from rooms.api.views import RoomListView


urlpatterns = [
    path("", RoomListView.as_view(), name="room-list"),
]
