from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse


class TestSensorsDataView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("backend:sensors_data")

    def test_returns_cached_data_sorted_by_key(self):
        cached_data = {
            "38:1F:8D:B2:1F:44": {"name": "TH05-B21F44"},
            "38:1F:8D:65:E9:1C": {"name": "TH05-65E91C"},
        }

        with patch("sensors.views.cache.get", return_value=cached_data):
            response = self.client.get(self.url)

        assert response.status_code == 200
        assert list(response.json().keys()) == [
            "38:1F:8D:65:E9:1C",
            "38:1F:8D:B2:1F:44",
        ]
        assert response.json() == cached_data

    def test_returns_default_placeholder_when_cache_is_empty(self):
        with patch("sensors.views.cache.get", return_value={"no": "data"}):
            response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.json() == {"no": "data"}
