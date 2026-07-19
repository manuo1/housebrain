import pytest
from core.utils.env_utils import environment_is_development


@pytest.mark.parametrize(
    "environment_value, expected",
    [
        ("development", True),
        ("production", False),
        ("staging", False),
        ("", False),
    ],
)
def test_environment_is_development_with_value_set(monkeypatch, environment_value, expected):
    monkeypatch.setenv("ENVIRONMENT", environment_value)
    assert environment_is_development() is expected


def test_environment_is_development_defaults_to_development_when_unset(monkeypatch):
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    assert environment_is_development() is True
