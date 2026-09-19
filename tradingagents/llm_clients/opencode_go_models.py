"""Reviewed OpenCode Go model metadata.

The official Go endpoint table assigns each model to one of three incompatible
wire protocols. Keep that fact in a dependency-free module so both the CLI
catalog and the lazy client factory use the same source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OpenCodeGoProtocol = Literal["chat_completions", "responses", "messages"]


@dataclass(frozen=True)
class OpenCodeGoModelSpec:
    """One Go model and the request protocol documented for it."""

    protocol: OpenCodeGoProtocol
    supports_tools: bool = False
    supports_forced_tool_choice: bool = False
    supports_structured_output: bool = False


# Source: https://opencode.ai/docs/go/ (reviewed 2026-09-19).
# New models must be added only after their endpoint/protocol is verified.
OPENCODE_GO_MODELS: dict[str, OpenCodeGoModelSpec] = {
    "grok-4.6": OpenCodeGoModelSpec("responses"),
    "gpt-5.6-luna": OpenCodeGoModelSpec("responses"),
    "muse-spark-1.3-contributor": OpenCodeGoModelSpec("responses"),
    "muse-spark-1.2-contributor": OpenCodeGoModelSpec("responses"),
    "glm-5.3-flash": OpenCodeGoModelSpec("chat_completions"),
    "glm-5.3": OpenCodeGoModelSpec("chat_completions"),
    "glm-5.2": OpenCodeGoModelSpec("chat_completions"),
    "glm-5.1": OpenCodeGoModelSpec("chat_completions"),
    "kimi-k3": OpenCodeGoModelSpec("chat_completions"),
    "kimi-k2.7-code": OpenCodeGoModelSpec("chat_completions"),
    "kimi-k2.6": OpenCodeGoModelSpec("chat_completions"),
    "longcat-2.0": OpenCodeGoModelSpec("chat_completions"),
    "deepseek-v4.1-flash": OpenCodeGoModelSpec("chat_completions"),
    "deepseek-v4-pro": OpenCodeGoModelSpec("chat_completions"),
    "deepseek-v4-flash": OpenCodeGoModelSpec("chat_completions"),
    "deepseek-v4-flash-vision-exp": OpenCodeGoModelSpec("chat_completions"),
    "mimo-v2.5": OpenCodeGoModelSpec("chat_completions"),
    "mimo-v2.5-pro": OpenCodeGoModelSpec("chat_completions"),
    "hy4-preview": OpenCodeGoModelSpec("chat_completions"),
    "hy3": OpenCodeGoModelSpec("chat_completions"),
    # Direct simulated contract coverage and a neutral live protocol probe
    # confirm this exact model accepts normal tools and a named tool choice.
    "minimax-m3": OpenCodeGoModelSpec("messages", True, True, True),
    "minimax-m2.7": OpenCodeGoModelSpec("messages"),
    "minimax-m2.5": OpenCodeGoModelSpec("messages"),
    "qwen3.8-max": OpenCodeGoModelSpec("messages"),
    # Qwen accepts ordinary tools, but the neutral live probe returned HTTP
    # 400 for a named forced tool. Do not infer that Minimax capability here.
    "qwen3.8-flash": OpenCodeGoModelSpec("messages", True, False, False),
    "qwen3.7-max": OpenCodeGoModelSpec("messages"),
    "qwen3.7-plus": OpenCodeGoModelSpec("messages"),
    "qwen3.6-plus": OpenCodeGoModelSpec("messages"),
}


def get_opencode_go_model_options() -> list[tuple[str, str]]:
    """Return the fixed, protocol-labelled Go model picker options."""
    return [
        (f"{model_id} ({spec.protocol.replace('_', ' ')})", model_id)
        for model_id, spec in OPENCODE_GO_MODELS.items()
    ]
