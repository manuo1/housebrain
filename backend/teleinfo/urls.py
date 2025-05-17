from django.urls import path
from . import views

urlpatterns = [
    path("data/", views.teleinfo_monitor, name="teleinfo_monitor"),
]
