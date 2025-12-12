from authentication.api.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    logout_view,
    user_info,
)
from django.urls import path

urlpatterns = [
    path("login/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", user_info, name="user_info"),
    path("logout/", logout_view, name="logout"),
]
