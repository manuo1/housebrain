from django.urls import path

from . import views

urlpatterns = [
    path("indexes/<str:date>/", views.indexes, name="indexes"),
]
