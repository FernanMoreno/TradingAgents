"""OpenCode Go adapter using the documented protocol for each model.

This module is intentionally a direct API adapter. It does not invoke the
OpenCode CLI, inspect OpenCode credential files, or select a separate OpenCode
product/a different provider after a failure.
"""

from __future__ import annotations

import os
from typing import Any

from .base_client import BaseLLMClient
from .openai_client import NormalizedChatOpenAI
from .opencode_go_messages import OpenCodeGoMessages
from .opencode_go_models import OPENCODE_GO_MODELS, OpenCodeGoModelSpec

OPENCODE_GO_API_BASE_URL = "https://opencode.ai/zen/go/v1"
OPENCODE_GO_API_KEY_ENV = "OPENCODE_GO_API_KEY"
OPENCODE_GO_USER_AGENT = "tradingagents/0.5.0"


class OpenCodeGoError(RuntimeError):
    """Base error for a Go request that must not trigger provider fallback."""

    is_terminal_provider_error = True


class OpenCodeGoConfigurationError(OpenCodeGoError):
    """Configuration prevents a Go request before a network client is used."""


class OpenCodeGoAuthenticationError(OpenCodeGoError):
    """Go rejected the configured authentication without exposing the key."""


class OpenCodeGoModelAvailabilityError(OpenCodeGoError):
    """Go denied access to a model whose availability is region-limited."""


class OpenCodeGoQuotaError(OpenCodeGoError):
    """Go rate or usage limit was exhausted; the run must stop."""


def _status_code(error: Exception) -> int | None:
    """Read a status code from SDK errors without depending on one SDK type."""
    direct = getattr(error, "status_code", None)
    if isinstance(direct, int):
        return direct
    response = getattr(error, "response", None)
    status = getattr(response, "status_code", None)
    return status if isinstance(status, int) else None


def classify_opencode_go_error(error: Exception, *, model: str | None = None) -> Exception:
    """Map auth/quota HTTP errors to stable, redacted errors.

    Other errors preserve their original type and traceback. Error bodies are
    deliberately not interpolated because they may echo an authorization header.
    """
    status = _status_code(error)
    if status == 403 and (spec := OPENCODE_GO_MODELS.get(model or "")) and spec.limited_regions:
        return OpenCodeGoModelAvailabilityError(
            f"OpenCode Go denied access to {model!r}. This model is documented as available only "
            "in limited regions; check regional availability and subscription access. "
            "The run stopped; no fallback was used."
        )
    if status in (401, 403):
        return OpenCodeGoAuthenticationError(
            "OpenCode Go authentication failed. Check OPENCODE_GO_API_KEY and subscription access."
        )
    if status == 429:
        return OpenCodeGoQuotaError(
            "OpenCode Go quota or rate limit was reached. The run stopped; no fallback was used."
        )
    return error


class _OpenCodeGoErrorMixin:
    """Normalize Go auth/quota errors while retaining LangChain's public API."""

    def invoke(self, input, config=None, **kwargs):
        try:
            return super().invoke(input, config, **kwargs)
        except Exception as error:
            classified = classify_opencode_go_error(error, model=self.model_name)
            if classified is error:
                raise
            raise classified from error


class OpenCodeGoChatOpenAI(_OpenCodeGoErrorMixin, NormalizedChatOpenAI):
    """OpenAI-compatible Go client for Chat Completions and Responses models."""


_PASSTHROUGH_KWARGS = (
    "timeout",
    "temperature",
    "max_tokens",
    "callbacks",
    "http_client",
    "http_async_client",
)


class OpenCodeGoClient(BaseLLMClient):
    """Build a Go client for the selected official model without fallback."""

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        session_id: str | None = None,
        **kwargs,
    ):
        super().__init__(model, base_url, **kwargs)
        self.session_id = session_id or kwargs.pop("opencode_go_session_id", None)

    def _model_spec(self) -> OpenCodeGoModelSpec:
        spec = OPENCODE_GO_MODELS.get(self.model)
        if spec is None:
            raise OpenCodeGoConfigurationError(
                f"Unsupported OpenCode Go model {self.model!r}. "
                "Choose a model listed by the OpenCode Go provider."
            )
        return spec

    def _api_key(self) -> str:
        key = os.environ.get(OPENCODE_GO_API_KEY_ENV)
        if not key:
            raise OpenCodeGoConfigurationError(
                "OpenCode Go requires OPENCODE_GO_API_KEY. Set it in your environment or .env file."
            )
        return key

    def _headers(self) -> dict[str, str]:
        if not self.session_id:
            raise OpenCodeGoConfigurationError(
                "OpenCode Go requires a stable session ID for this run."
            )
        return {
            "User-Agent": OPENCODE_GO_USER_AGENT,
            "x-opencode-session": self.session_id,
        }

    def _base_kwargs(self) -> dict[str, Any]:
        if self.base_url and self.base_url.rstrip("/") != OPENCODE_GO_API_BASE_URL:
            raise OpenCodeGoConfigurationError(
                "OpenCode Go does not support a custom backend_url. "
                f"Use {OPENCODE_GO_API_BASE_URL}."
            )
        kwargs: dict[str, Any] = {
            "model": self.model,
            "base_url": OPENCODE_GO_API_BASE_URL,
            "api_key": self._api_key(),
            "default_headers": self._headers(),
            # A Go 429 denotes a usage/rate limit. Retrying it would spend more
            # requests before surfacing the required terminal quota error.
            "max_retries": 0,
        }
        for key in _PASSTHROUGH_KWARGS:
            if key in self.kwargs:
                kwargs[key] = self.kwargs[key]
        return kwargs

    def get_llm(self) -> Any:
        """Return the matching LangChain client for this model's Go protocol."""
        spec = self._model_spec()
        kwargs = self._base_kwargs()
        if spec.protocol == "chat_completions":
            return OpenCodeGoChatOpenAI(**kwargs)
        if spec.protocol == "responses":
            return OpenCodeGoChatOpenAI(use_responses_api=True, **kwargs)
        if spec.protocol == "messages":
            kwargs["base_url"] = f"{OPENCODE_GO_API_BASE_URL}/messages"
            return OpenCodeGoMessages(
                **kwargs,
                supports_tools=spec.supports_tools,
                supports_forced_tool_choice=spec.supports_forced_tool_choice,
                supports_structured_output=spec.supports_structured_output,
                error_classifier=classify_opencode_go_error,
            )
        raise OpenCodeGoConfigurationError(
            f"OpenCode Go model {self.model!r} has an unsupported protocol {spec.protocol!r}."
        )

    def validate_model(self) -> bool:
        """Only officially reviewed Go model IDs are accepted."""
        return self.model in OPENCODE_GO_MODELS
