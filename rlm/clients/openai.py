import os
from collections import defaultdict
from typing import Any

import openai
from dotenv import load_dotenv

from rlm.clients.base_lm import BaseLM
from rlm.core.types import ModelUsageSummary, UsageSummary

load_dotenv()

OPENAI_MODEL_ENV_VARS = (
    "OPENAI_MODEL",
    "OPENAI_MODEL_NAME",
    "RLM_MODEL_NAME",
    "MODEL_NAME",
)
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
VERCEL_BASE_URL = "https://ai-gateway.vercel.sh/v1"
DEFAULT_PRIME_INTELLECT_BASE_URL = "https://api.pinference.ai/api/v1/"


def _normalize_base_url(base_url: str | None) -> str | None:
    return base_url.rstrip("/") if base_url else None


def _resolve_model_name(model_name: str | None) -> str | None:
    if model_name:
        return model_name
    for env_var in OPENAI_MODEL_ENV_VARS:
        value = os.getenv(env_var)
        if value:
            return value
    return None


def _resolve_api_key(base_url: str | None, api_key: str | None) -> tuple[str | None, str]:
    if api_key:
        return api_key, "(explicit api_key argument)"

    normalized_base_url = _normalize_base_url(base_url)
    if normalized_base_url == _normalize_base_url(OPENROUTER_BASE_URL):
        return os.getenv("OPENROUTER_API_KEY"), "OPENROUTER_API_KEY"
    if normalized_base_url == _normalize_base_url(VERCEL_BASE_URL):
        return os.getenv("AI_GATEWAY_API_KEY"), "AI_GATEWAY_API_KEY"
    if normalized_base_url == _normalize_base_url(DEFAULT_PRIME_INTELLECT_BASE_URL):
        return os.getenv("PRIME_API_KEY"), "PRIME_API_KEY"
    return os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY"


def _is_valid_base_url(base_url: str) -> bool:
    return base_url.startswith("http://") or base_url.startswith("https://")


class OpenAIClient(BaseLM):
    """
    LM Client for running models with the OpenAI API. Works with vLLM as well.

    Any additional keyword arguments (e.g. default_headers, default_query, max_retries)
    are passed through to the underlying openai.OpenAI and openai.AsyncOpenAI constructors.
    Only model_name is excluded, since it is not a client constructor argument.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ):
        super().__init__(model_name=model_name or "unknown", **kwargs)

        base_url = base_url or os.getenv("OPENAI_BASE_URL")
        if base_url and not _is_valid_base_url(base_url):
            raise ValueError(
                "Invalid OpenAI base_url. Expected a full URL beginning with http:// or https:// "
                "(for example, 'http://localhost:1234/v1'). "
                "Set OPENAI_BASE_URL in .env or pass base_url in backend_kwargs."
            )

        api_key, api_key_source = _resolve_api_key(base_url, api_key)
        if not api_key:
            raise ValueError(
                f"OpenAI API key is required but was not found from {api_key_source}. "
                "Set it in .env or pass api_key in backend_kwargs."
            )

        model_name = _resolve_model_name(model_name)

        # Pass through arbitrary kwargs to the OpenAI client (e.g. default_headers, default_query, max_retries).
        # Exclude model_name since it is not an OpenAI client constructor argument.
        client_kwargs = {
            "api_key": api_key,
            "base_url": base_url,
            "timeout": self.timeout,
            **{k: v for k, v in self.kwargs.items() if k != "model_name"},
        }
        self.client = openai.OpenAI(**client_kwargs)
        self.async_client = openai.AsyncOpenAI(**client_kwargs)
        self.model_name = model_name
        self.base_url = base_url  # Track for cost extraction

        # Per-model usage tracking
        self.model_call_counts: dict[str, int] = defaultdict(int)
        self.model_input_tokens: dict[str, int] = defaultdict(int)
        self.model_output_tokens: dict[str, int] = defaultdict(int)
        self.model_total_tokens: dict[str, int] = defaultdict(int)
        self.model_costs: dict[str, float] = defaultdict(float)  # Cost in USD

    def completion(self, prompt: str | list[dict[str, Any]], model: str | None = None) -> str:
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list) and all(isinstance(item, dict) for item in prompt):
            messages = prompt
        else:
            raise ValueError(f"Invalid prompt type: {type(prompt)}")

        model = model or self.model_name
        if not model:
            raise ValueError(
                "Model name is required for OpenAI client. "
                "Set backend_kwargs['model_name'] or set one of these .env vars: "
                f"{', '.join(OPENAI_MODEL_ENV_VARS)}"
            )

        extra_body = {}
        if _normalize_base_url(str(self.client.base_url)) == _normalize_base_url(
            DEFAULT_PRIME_INTELLECT_BASE_URL
        ):
            extra_body["usage"] = {"include": True}

        response = self.client.chat.completions.create(
            model=model, messages=messages, extra_body=extra_body
        )
        self._track_cost(response, model)
        return response.choices[0].message.content or ""

    async def acompletion(
        self, prompt: str | list[dict[str, Any]], model: str | None = None
    ) -> str:
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list) and all(isinstance(item, dict) for item in prompt):
            messages = prompt
        else:
            raise ValueError(f"Invalid prompt type: {type(prompt)}")

        model = model or self.model_name
        if not model:
            raise ValueError(
                "Model name is required for OpenAI client. "
                "Set backend_kwargs['model_name'] or set one of these .env vars: "
                f"{', '.join(OPENAI_MODEL_ENV_VARS)}"
            )

        extra_body = {}
        if _normalize_base_url(str(self.client.base_url)) == _normalize_base_url(
            DEFAULT_PRIME_INTELLECT_BASE_URL
        ):
            extra_body["usage"] = {"include": True}

        response = await self.async_client.chat.completions.create(
            model=model, messages=messages, extra_body=extra_body
        )
        self._track_cost(response, model)
        return response.choices[0].message.content or ""

    def _track_cost(self, response: Any, model: str):
        self.model_call_counts[model] += 1

        usage = getattr(response, "usage", None)
        if usage is None:
            raise ValueError("No usage data received. Tracking tokens not possible.")

        self.model_input_tokens[model] += usage.prompt_tokens
        self.model_output_tokens[model] += usage.completion_tokens
        self.model_total_tokens[model] += usage.total_tokens

        # Track last call for handler to read
        self.last_prompt_tokens = usage.prompt_tokens
        self.last_completion_tokens = usage.completion_tokens

        # Extract cost from OpenRouter responses (cost is in USD)
        # OpenRouter returns cost in usage.model_extra for pydantic models
        self.last_cost: float | None = None
        cost = None

        # Try direct attribute first
        if hasattr(usage, "cost") and usage.cost:
            cost = usage.cost
        # Then try model_extra (OpenRouter uses this)
        elif hasattr(usage, "model_extra") and usage.model_extra:
            extra = usage.model_extra
            # Primary cost field (may be 0 for BYOK)
            if extra.get("cost"):
                cost = extra["cost"]
            # Fallback to upstream cost details
            elif extra.get("cost_details", {}).get("upstream_inference_cost"):
                cost = extra["cost_details"]["upstream_inference_cost"]

        if cost is not None and cost > 0:
            self.last_cost = float(cost)
            self.model_costs[model] += self.last_cost

    def get_usage_summary(self) -> UsageSummary:
        model_summaries = {}
        for model in self.model_call_counts:
            cost = self.model_costs.get(model)
            model_summaries[model] = ModelUsageSummary(
                total_calls=self.model_call_counts[model],
                total_input_tokens=self.model_input_tokens[model],
                total_output_tokens=self.model_output_tokens[model],
                total_cost=cost if cost else None,
            )
        return UsageSummary(model_usage_summaries=model_summaries)

    def get_last_usage(self) -> ModelUsageSummary:
        return ModelUsageSummary(
            total_calls=1,
            total_input_tokens=self.last_prompt_tokens,
            total_output_tokens=self.last_completion_tokens,
            total_cost=getattr(self, "last_cost", None),
        )
