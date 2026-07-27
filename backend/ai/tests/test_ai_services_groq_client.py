from unittest.mock import MagicMock, patch

import httpx
import pytest
from groq import APIError, RateLimitError
from rest_framework.exceptions import ValidationError as DRFValidationError

from ai.services.groq_client import GroqClient, _parse_retry_delay


def _fake_response(status_code=429):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    return httpx.Response(status_code, request=request)


def _rate_limit_error(message):
    return RateLimitError(message, response=_fake_response(429), body=None)


def _api_error(message):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    return APIError(message, request, body=None)


# ------------------------------------------------------------------------------
# _parse_retry_delay
# ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "error_message, expected",
    [
        ("Please try again in 58m46.848s.", "58 minutes"),
        ("Please try again in 1m2s.", "1 minute"),
        ("Please try again in 45.2s.", "moins d'une minute"),
        ("Some unrelated error message", None),
    ],
)
def test_parse_retry_delay(error_message, expected):
    assert _parse_retry_delay(error_message) == expected


# ------------------------------------------------------------------------------
# GroqClient.__init__
# ------------------------------------------------------------------------------


def test_init_raises_when_api_key_is_not_set():
    with patch("ai.services.groq_client.settings.GROQ_API_KEY", ""):
        with pytest.raises(ValueError, match="GROQ_API_KEY is not set"):
            GroqClient()


def test_init_succeeds_when_api_key_is_set():
    with patch("ai.services.groq_client.settings.GROQ_API_KEY", "fake-key"):
        client = GroqClient()
        assert client.client is not None


# ------------------------------------------------------------------------------
# GroqClient.generate
# ------------------------------------------------------------------------------


def _make_client_with_mocked_sdk():
    with patch("ai.services.groq_client.settings.GROQ_API_KEY", "fake-key"):
        client = GroqClient()
    client.client = MagicMock()
    return client


def test_generate_returns_message_content_on_success():
    client = _make_client_with_mocked_sdk()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"success": true}'
    client.client.chat.completions.create.return_value = mock_response

    result = client.generate("system prompt", "user prompt")

    assert result == '{"success": true}'
    client.client.chat.completions.create.assert_called_once()
    call_kwargs = client.client.chat.completions.create.call_args.kwargs
    assert call_kwargs["messages"] == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "user prompt"},
    ]


def test_generate_raises_validation_error_with_retry_delay_on_rate_limit():
    client = _make_client_with_mocked_sdk()
    client.client.chat.completions.create.side_effect = _rate_limit_error(
        "Please try again in 58m46.848s."
    )

    with pytest.raises(DRFValidationError) as excinfo:
        client.generate("system prompt", "user prompt")

    assert "58 minutes" in str(excinfo.value.detail)


def test_generate_raises_validation_error_without_retry_delay_when_unparseable():
    client = _make_client_with_mocked_sdk()
    client.client.chat.completions.create.side_effect = _rate_limit_error(
        "Rate limit reached, no delay info"
    )

    with pytest.raises(DRFValidationError) as excinfo:
        client.generate("system prompt", "user prompt")

    assert "Réessayez plus tard" in str(excinfo.value.detail)


def test_generate_raises_validation_error_on_api_error():
    client = _make_client_with_mocked_sdk()
    client.client.chat.completions.create.side_effect = _api_error("boom")

    with pytest.raises(DRFValidationError) as excinfo:
        client.generate("system prompt", "user prompt")

    assert "temporairement indisponible" in str(excinfo.value.detail)


def test_generate_raises_validation_error_on_unexpected_exception():
    client = _make_client_with_mocked_sdk()
    client.client.chat.completions.create.side_effect = RuntimeError("boom")

    with pytest.raises(DRFValidationError) as excinfo:
        client.generate("system prompt", "user prompt")

    assert "erreur inattendue" in str(excinfo.value.detail)
