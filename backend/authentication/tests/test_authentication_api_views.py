import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

REFRESH_COOKIE_PATH = "/api/auth/refresh/"


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    # ScopedRateThrottle counters live in the default cache; reset before
    # each test so tests don't leak into each other's rate limit window.
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def authenticated_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


# ------------------------------------------------------------------------------
# login
# ------------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_success_sets_cookie_and_returns_access_token(api_client, user):
    response = api_client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "testpass123"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" not in response.data

    cookie = response.cookies["refresh_token"]
    assert cookie.value
    assert cookie["path"] == REFRESH_COOKIE_PATH
    assert cookie["httponly"] is True
    assert cookie["samesite"] == "Strict"


@pytest.mark.django_db
def test_login_wrong_credentials(api_client, user):
    response = api_client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "wrongpass"},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "refresh_token" not in response.cookies or not response.cookies["refresh_token"].value


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload",
    [
        {"username": "testuser"},
        {"password": "testpass123"},
        {},
    ],
)
def test_login_missing_fields(api_client, user, payload):
    response = api_client.post("/api/auth/login/", payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_is_throttled_after_five_attempts_per_minute(api_client, user):
    for _ in range(5):
        response = api_client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "wrongpass"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = api_client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "wrongpass"},
        format="json",
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


# ------------------------------------------------------------------------------
# refresh
# ------------------------------------------------------------------------------


@pytest.mark.django_db
def test_refresh_success_with_valid_cookie(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.cookies["refresh_token"] = str(refresh)

    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


@pytest.mark.django_db
def test_refresh_missing_cookie(api_client):
    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing refresh token" in response.data["detail"]


@pytest.mark.django_db
def test_refresh_invalid_cookie(api_client):
    api_client.cookies["refresh_token"] = "not-a-valid-token"

    response = api_client.post("/api/auth/refresh/", format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid or expired" in response.data["detail"]


# ------------------------------------------------------------------------------
# logout
# ------------------------------------------------------------------------------


def test_logout_clears_cookie_and_is_accessible_without_auth(api_client):
    response = api_client.post("/api/auth/logout/", format="json")

    assert response.status_code == status.HTTP_200_OK
    cookie = response.cookies["refresh_token"]
    # Deleted cookies get an empty value and an expiry in the past
    assert cookie.value == ""
    assert cookie["path"] == REFRESH_COOKIE_PATH


# ------------------------------------------------------------------------------
# me (user_info)
# ------------------------------------------------------------------------------


@pytest.mark.django_db
def test_me_authenticated_returns_username(authenticated_client, user):
    response = authenticated_client.get("/api/auth/me/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == "testuser"


def test_me_unauthenticated(api_client):
    response = api_client.get("/api/auth/me/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
