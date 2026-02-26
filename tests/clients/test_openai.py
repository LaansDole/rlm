"""Unit tests for OpenAI client configuration behavior."""

from unittest.mock import patch

import pytest

from rlm.clients import get_client
from rlm.clients.openai import OpenAIClient


class TestOpenAIClientConfig:
    """Tests for .env-driven OpenAI client setup and validation."""

    def test_init_uses_env_base_url_model_and_api_key(self):
        with patch("rlm.clients.openai.openai.OpenAI") as mock_openai:
            with patch("rlm.clients.openai.openai.AsyncOpenAI"):
                with patch.dict(
                    "os.environ",
                    {
                        "OPENAI_BASE_URL": "http://localhost:1234/v1",
                        "OPENAI_API_KEY": "lm-studio",
                        "OPENAI_MODEL": "qwen/qwen-8b",
                    },
                    clear=True,
                ):
                    client = OpenAIClient()

                    assert client.base_url == "http://localhost:1234/v1"
                    assert client.model_name == "qwen/qwen-8b"
                    kwargs = mock_openai.call_args[1]
                    assert kwargs["base_url"] == "http://localhost:1234/v1"
                    assert kwargs["api_key"] == "lm-studio"

    def test_init_uses_model_name_convention_fallback(self):
        with patch("rlm.clients.openai.openai.OpenAI"):
            with patch("rlm.clients.openai.openai.AsyncOpenAI"):
                with patch.dict(
                    "os.environ",
                    {
                        "OPENAI_API_KEY": "test-key",
                        "MODEL_NAME": "qwen/qwen-8b",
                    },
                    clear=True,
                ):
                    client = OpenAIClient()
                    assert client.model_name == "qwen/qwen-8b"

    def test_init_requires_api_key_with_actionable_error(self):
        with patch("rlm.clients.openai.openai.OpenAI"):
            with patch("rlm.clients.openai.openai.AsyncOpenAI"):
                with patch.dict("os.environ", {}, clear=True):
                    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                        OpenAIClient(model_name="qwen/qwen-8b")

    def test_init_rejects_invalid_base_url(self):
        with patch("rlm.clients.openai.openai.OpenAI"):
            with patch("rlm.clients.openai.openai.AsyncOpenAI"):
                with pytest.raises(ValueError, match="http:// or https://"):
                    OpenAIClient(
                        api_key="test-key",
                        model_name="qwen/qwen-8b",
                        base_url="localhost:1234/v1",
                    )

    def test_completion_requires_model_with_actionable_error(self):
        with patch("rlm.clients.openai.openai.OpenAI"):
            with patch("rlm.clients.openai.openai.AsyncOpenAI"):
                client = OpenAIClient(api_key="test-key", model_name=None)
                with pytest.raises(ValueError, match=r"backend_kwargs\['model_name'\]"):
                    client.completion("hello")


def test_get_client_accepts_none_backend_kwargs_for_openai():
    with patch("rlm.clients.openai.openai.OpenAI"):
        with patch("rlm.clients.openai.openai.AsyncOpenAI"):
            with patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-key",
                    "OPENAI_MODEL": "qwen/qwen-8b",
                },
                clear=True,
            ):
                client = get_client("openai", None)
                assert isinstance(client, OpenAIClient)
