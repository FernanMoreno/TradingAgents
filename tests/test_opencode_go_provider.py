"""Simulated contract tests for the OpenCode Go provider.

These tests never call OpenCode, Zen, another LLM provider, or financial data.
They use constructors and an in-process HTTP mock only.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

import httpx
import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from pydantic import BaseModel

try:  # Anthropic SDK 0.8x uses its vendored-compatible httpx2 transport.
    import httpx2
except ModuleNotFoundError:  # Older supported Anthropic SDKs use httpx itself.
    httpx2 = httpx

from cli.prefs import sanitize
from cli.utils import _llm_provider_table
from tradingagents.agents.utils.structured import bind_structured
from tradingagents.llm_clients.api_key_env import get_api_key_env
from tradingagents.llm_clients.factory import create_llm_client
from tradingagents.llm_clients.model_catalog import get_model_options
from tradingagents.llm_clients.opencode_go_client import (
    OPENCODE_GO_API_BASE_URL,
    OPENCODE_GO_MODELS,
    OPENCODE_GO_USER_AGENT,
    OpenCodeGoAuthenticationError,
    OpenCodeGoClient,
    OpenCodeGoConfigurationError,
    OpenCodeGoModelAvailabilityError,
    OpenCodeGoQuotaError,
    classify_opencode_go_error,
)
from tradingagents.llm_clients.opencode_go_messages import OpenCodeGoProtocolError
from tradingagents.llm_clients.validators import validate_model


class _FakeOpenAIProtocolClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def bind_tools(self, tools):
        return ("tools", tools)

    def with_structured_output(self, schema):
        return ("structured", schema)


class _FakeMessagesProtocolClient(_FakeOpenAIProtocolClient):
    pass


class _Decision(BaseModel):
    rating: str


@dataclass
class _FakeStatusError(Exception):
    status_code: int
    message: str

    def __str__(self) -> str:
        return self.message


@pytest.mark.unit
@pytest.mark.parametrize(
    ("model", "protocol"),
    [
        ("glm-5.3-flash", "chat_completions"),
        ("gpt-5.6-luna", "responses"),
        ("qwen3.8-flash", "messages"),
    ],
)
def test_official_go_models_have_an_explicit_protocol(model, protocol):
    assert OPENCODE_GO_MODELS[model].protocol == protocol


@pytest.mark.unit
def test_go_model_catalog_is_strict_and_exposed_to_the_cli():
    assert validate_model("opencode_go", "glm-5.3-flash") is True
    assert validate_model("opencode_go", "not-a-go-model") is False
    offered = {model for _, model in get_model_options("opencode_go", "quick")}
    assert "glm-5.3-flash" in offered
    assert "custom" not in offered


@pytest.mark.unit
def test_go_quick_catalog_excludes_messages_models_without_ordinary_tools():
    """A menu selection must not reach the analyst tool-binding failure."""
    no_tool_messages_models = {
        "minimax-m2.7",
        "minimax-m2.5",
        "qwen3.8-max",
        "qwen3.7-max",
        "qwen3.7-plus",
        "qwen3.6-plus",
    }

    quick = {model for _, model in get_model_options("opencode_go", "quick")}
    deep = {model for _, model in get_model_options("opencode_go", "deep")}

    assert no_tool_messages_models.isdisjoint(quick)
    assert no_tool_messages_models <= deep
    assert {"minimax-m3", "qwen3.8-flash"} <= quick


@pytest.mark.unit
def test_saved_go_quick_model_without_tools_is_not_reused():
    saved = {
        "llm_provider": "opencode_go",
        "quick_think_llm": "qwen3.7-plus",
        "deep_think_llm": "qwen3.7-plus",
    }

    restored = sanitize(saved, "stock")

    assert "quick_think_llm" not in restored
    assert restored["deep_think_llm"] == "qwen3.7-plus"


@pytest.mark.unit
@pytest.mark.parametrize(
    "model",
    [
        "minimax-m2.7",
        "minimax-m2.5",
        "qwen3.8-max",
        "qwen3.7-max",
        "qwen3.7-plus",
        "qwen3.6-plus",
    ],
)
def test_go_quick_model_without_tools_fails_before_graph_initialization(monkeypatch, model):
    """Direct or environment configuration must fail before any startup work."""
    import tradingagents.graph.trading_graph as graph_module

    config = {
        "llm_provider": "opencode_go",
        "quick_think_llm": model,
        "deep_think_llm": "minimax-m3",
    }
    monkeypatch.setattr(
        graph_module,
        "set_config",
        lambda _: pytest.fail("invalid Go quick configuration changed shared configuration"),
    )
    monkeypatch.setattr(
        graph_module.os,
        "makedirs",
        lambda *_args, **_kwargs: pytest.fail("invalid Go quick configuration created a directory"),
    )
    monkeypatch.setattr(
        graph_module,
        "create_llm_client",
        lambda **_kwargs: pytest.fail("invalid Go quick configuration built an AI client"),
    )

    with pytest.raises(OpenCodeGoConfigurationError, match="quick_think_llm.*ordinary tools"):
        graph_module.TradingAgentsGraph(config=config)


@pytest.mark.unit
def test_go_key_has_its_own_environment_variable():
    assert get_api_key_env("opencode_go") == "OPENCODE_GO_API_KEY"


@pytest.mark.unit
def test_go_is_an_explicit_cli_provider_choice():
    assert ("OpenCode Go", "opencode_go", OPENCODE_GO_API_BASE_URL) in _llm_provider_table()


@pytest.mark.unit
def test_factory_selects_go_without_selecting_another_provider():
    client = create_llm_client("opencode_go", "glm-5.3-flash")
    assert isinstance(client, OpenCodeGoClient)


@pytest.mark.unit
def test_missing_go_key_fails_before_constructing_a_protocol_client(monkeypatch):
    import tradingagents.llm_clients.opencode_go_client as go

    monkeypatch.delenv("OPENCODE_GO_API_KEY", raising=False)
    monkeypatch.setattr(
        go,
        "OpenCodeGoChatOpenAI",
        lambda **_: pytest.fail("a missing key must not construct a network client"),
    )

    with pytest.raises(OpenCodeGoConfigurationError, match="OPENCODE_GO_API_KEY"):
        OpenCodeGoClient("glm-5.3-flash", session_id="run-1").get_llm()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("model", "expected_type", "responses", "expected_base_url"),
    [
        ("glm-5.3-flash", _FakeOpenAIProtocolClient, False, OPENCODE_GO_API_BASE_URL),
        ("gpt-5.6-luna", _FakeOpenAIProtocolClient, True, OPENCODE_GO_API_BASE_URL),
        (
            "qwen3.8-flash",
            _FakeMessagesProtocolClient,
            False,
            f"{OPENCODE_GO_API_BASE_URL}/messages",
        ),
    ],
)
def test_protocol_constructor_uses_honest_identity_and_stable_session(
    monkeypatch, model, expected_type, responses, expected_base_url
):
    import tradingagents.llm_clients.opencode_go_client as go

    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    monkeypatch.setattr(go, "OpenCodeGoChatOpenAI", _FakeOpenAIProtocolClient)
    monkeypatch.setattr(go, "OpenCodeGoMessages", _FakeMessagesProtocolClient)

    llm = OpenCodeGoClient(model, session_id="stable-run-id").get_llm()

    assert isinstance(llm, expected_type)
    assert llm.kwargs["base_url"] == expected_base_url
    assert llm.kwargs["default_headers"] == {
        "User-Agent": OPENCODE_GO_USER_AGENT,
        "x-opencode-session": "stable-run-id",
    }
    assert llm.kwargs["api_key"] == "fake-go-key"
    assert llm.kwargs["max_retries"] == 0
    assert llm.kwargs.get("use_responses_api", False) is responses


@pytest.mark.unit
def test_go_protocol_clients_retain_tool_and_structured_output_methods(monkeypatch):
    import tradingagents.llm_clients.opencode_go_client as go

    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    monkeypatch.setattr(go, "OpenCodeGoChatOpenAI", _FakeOpenAIProtocolClient)

    llm = OpenCodeGoClient("glm-5.3-flash", session_id="run-1").get_llm()

    assert llm.bind_tools(["market_tool"]) == ("tools", ["market_tool"])
    assert llm.with_structured_output(dict) == ("structured", dict)


@pytest.mark.unit
def test_go_rejects_a_custom_backend_before_constructing_a_protocol_client(monkeypatch):
    import tradingagents.llm_clients.opencode_go_client as go

    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    monkeypatch.setattr(
        go,
        "OpenCodeGoChatOpenAI",
        lambda **_: pytest.fail("Go must never redirect to another backend"),
    )

    with pytest.raises(OpenCodeGoConfigurationError, match="custom backend_url"):
        OpenCodeGoClient(
            "glm-5.3-flash",
            base_url="https://api.example.invalid/v1",
            session_id="simulated-run",
        ).get_llm()


@pytest.mark.unit
def test_messages_reject_a_custom_backend_before_constructing_direct_transport(monkeypatch):
    import tradingagents.llm_clients.opencode_go_client as go

    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    monkeypatch.setattr(
        go,
        "OpenCodeGoMessages",
        lambda **_: pytest.fail("Go Messages must never redirect to another backend"),
    )

    with pytest.raises(OpenCodeGoConfigurationError, match="custom backend_url"):
        OpenCodeGoClient(
            "qwen3.8-flash",
            base_url="https://api.example.invalid/v1",
            session_id="simulated-run",
        ).get_llm()


@pytest.mark.unit
def test_messages_invokes_go_without_constructing_an_anthropic_client(monkeypatch):
    """The Go Messages branch owns its transport even though its wire format is compatible."""
    import tradingagents.llm_clients.opencode_go_client as go

    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    monkeypatch.setattr(
        go,
        "Anthropic",
        lambda **_: pytest.fail("Go Messages must not construct an Anthropic client"),
        raising=False,
    )
    requests = []

    def fake_go_gateway(request):
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={
                "id": "msg_simulated",
                "type": "message",
                "role": "assistant",
                "model": "qwen3.8-flash",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "DIRECT_GO_OK"}],
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    llm = OpenCodeGoClient(
        "qwen3.8-flash",
        session_id="simulated-run",
        http_client=httpx2.Client(transport=httpx2.MockTransport(fake_go_gateway)),
    ).get_llm()

    response = llm.invoke("simulated provider request")
    assert response.content == "DIRECT_GO_OK"
    assert response.usage_metadata == {
        "input_tokens": 1,
        "output_tokens": 1,
        "total_tokens": 2,
    }
    assert len(requests) == 1
    assert str(requests[0].url) == f"{OPENCODE_GO_API_BASE_URL}/messages"


@pytest.mark.unit
def test_messages_serializes_tools_and_parses_go_tool_use(monkeypatch):
    """Normal Go tool calls remain LangChain tool calls for analyst routing."""
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    @tool
    def simulated_lookup(symbol: str) -> str:
        """Return simulated context for one symbol."""
        return symbol

    def fake_go_gateway(request):
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={
                "id": "msg_tool_simulated",
                "type": "message",
                "role": "assistant",
                "model": "qwen3.8-flash",
                "stop_reason": "tool_use",
                "content": [
                    {"type": "text", "text": "Looking up context."},
                    {
                        "type": "tool_use",
                        "id": "toolu_simulated",
                        "name": "simulated_lookup",
                        "input": {"symbol": "SIM"},
                    },
                ],
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    llm = OpenCodeGoClient(
        "qwen3.8-flash",
        session_id="simulated-run",
        http_client=httpx2.Client(transport=httpx2.MockTransport(fake_go_gateway)),
    ).get_llm()

    result = llm.bind_tools([simulated_lookup]).invoke("simulated tool request")

    assert result.content == "Looking up context."
    assert result.tool_calls == [
        {
            "name": "simulated_lookup",
            "args": {"symbol": "SIM"},
            "id": "toolu_simulated",
            "type": "tool_call",
        }
    ]
    body = json.loads(requests[0].content)
    assert body["tools"] == [
        {
            "name": "simulated_lookup",
            "description": "Return simulated context for one symbol.",
            "input_schema": {
                "properties": {"symbol": {"type": "string"}},
                "required": ["symbol"],
                "type": "object",
            },
        }
    ]


@pytest.mark.unit
def test_messages_serializes_system_and_tool_result_history(monkeypatch):
    """A Go tool round-trip preserves the history emitted by LangGraph's ToolNode."""
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    def fake_go_gateway(request):
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={
                "id": "msg_follow_up_simulated",
                "type": "message",
                "role": "assistant",
                "model": "qwen3.8-flash",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "tool result considered"}],
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    llm = OpenCodeGoClient(
        "qwen3.8-flash",
        session_id="simulated-run",
        http_client=httpx2.Client(transport=httpx2.MockTransport(fake_go_gateway)),
    ).get_llm()

    result = llm.invoke(
        [
            SystemMessage("Simulated system prompt."),
            HumanMessage("Look up SIM."),
            AIMessage(
                "",
                tool_calls=[
                    {
                        "name": "simulated_lookup",
                        "args": {"symbol": "SIM"},
                        "id": "toolu_simulated",
                    }
                ],
            ),
            ToolMessage("simulated result", tool_call_id="toolu_simulated"),
        ]
    )

    assert result.content == "tool result considered"
    body = json.loads(requests[0].content)
    assert body["system"] == "Simulated system prompt."
    assert body["messages"] == [
        {"role": "user", "content": "Look up SIM."},
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_simulated",
                    "name": "simulated_lookup",
                    "input": {"symbol": "SIM"},
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "toolu_simulated",
                    "content": "simulated result",
                }
            ],
        },
    ]


@pytest.mark.unit
def test_messages_groups_parallel_tool_results_into_one_user_turn(monkeypatch):
    """A ToolNode batch stays one Messages tool-result turn."""
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    def fake_go_gateway(request):
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={
                "id": "msg_parallel_simulated",
                "type": "message",
                "role": "assistant",
                "model": "qwen3.8-flash",
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": "parallel results considered"}],
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    llm = OpenCodeGoClient(
        "qwen3.8-flash",
        session_id="simulated-run",
        http_client=httpx2.Client(transport=httpx2.MockTransport(fake_go_gateway)),
    ).get_llm()

    assert llm.invoke(
        [
            HumanMessage("Look up two simulated values."),
            AIMessage(
                "",
                tool_calls=[
                    {"name": "first_lookup", "args": {}, "id": "toolu_first"},
                    {"name": "second_lookup", "args": {}, "id": "toolu_second"},
                ],
            ),
            ToolMessage("first result", tool_call_id="toolu_first"),
            ToolMessage("second result", tool_call_id="toolu_second"),
        ]
    ).content == "parallel results considered"

    body = json.loads(requests[0].content)
    assert body["messages"][2] == {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "toolu_first", "content": "first result"},
            {"type": "tool_result", "tool_use_id": "toolu_second", "content": "second result"},
        ],
    }
    assert len(body["messages"]) == 3


@pytest.mark.unit
def test_qwen_messages_permits_non_forced_auto_tool_choice_without_transport(monkeypatch):
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    llm = OpenCodeGoClient("qwen3.8-flash", session_id="simulated-run").get_llm()

    assert llm.bind_tools([], tool_choice="auto") is not None
    assert llm.bind_tools([], tool_choice="any") is not None


@pytest.mark.unit
def test_messages_round_trips_go_thinking_blocks_before_a_tool_result(monkeypatch):
    """Thinking blocks from Go stay in the next assistant turn unchanged."""
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    @tool
    def simulated_lookup(symbol: str) -> str:
        """Return simulated context for one symbol."""
        return symbol

    def fake_go_gateway(request):
        requests.append(request)
        if len(requests) == 1:
            content = [
                {
                    "type": "thinking",
                    "thinking": "simulated private reasoning",
                    "signature": "simulated-signature",
                },
                {
                    "type": "tool_use",
                    "id": "toolu_thinking",
                    "name": "simulated_lookup",
                    "input": {"symbol": "SIM"},
                },
            ]
            stop_reason = "tool_use"
        else:
            content = [{"type": "text", "text": "tool result considered"}]
            stop_reason = "end_turn"
        return httpx2.Response(
            200,
            request=request,
            json={
                "id": f"msg_simulated_{len(requests)}",
                "type": "message",
                "role": "assistant",
                "model": "qwen3.8-flash",
                "stop_reason": stop_reason,
                "content": content,
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    llm = OpenCodeGoClient(
        "qwen3.8-flash",
        session_id="simulated-run",
        http_client=httpx2.Client(transport=httpx2.MockTransport(fake_go_gateway)),
    ).get_llm()
    initial = HumanMessage("Look up SIM.")
    tool_request = llm.bind_tools([simulated_lookup]).invoke([initial])

    assert tool_request.additional_kwargs["opencode_go_content_blocks"] == [
        {
            "type": "thinking",
            "thinking": "simulated private reasoning",
            "signature": "simulated-signature",
        }
    ]
    assert llm.invoke(
        [initial, tool_request, ToolMessage("simulated result", tool_call_id="toolu_thinking")]
    ).content == "tool result considered"
    follow_up = json.loads(requests[1].content)
    assert follow_up["messages"][1]["content"] == [
        {
            "type": "thinking",
            "thinking": "simulated private reasoning",
            "signature": "simulated-signature",
        },
        {
            "type": "tool_use",
            "id": "toolu_thinking",
            "name": "simulated_lookup",
            "input": {"symbol": "SIM"},
        },
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    "content",
    [
        {"not": "a list"},
        [{"type": "tool_use", "id": "toolu_bad", "name": "lookup", "input": []}],
        [{"type": "sensitive-unknown-block"}],
    ],
)
def test_messages_rejects_malformed_go_content_without_provider_fallback(monkeypatch, content):
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    def fake_go_gateway(request):
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={"id": "msg_bad", "model": "qwen3.8-flash", "content": content},
        )

    llm = OpenCodeGoClient(
        "qwen3.8-flash",
        session_id="simulated-run",
        http_client=httpx2.Client(transport=httpx2.MockTransport(fake_go_gateway)),
    ).get_llm()

    with pytest.raises(OpenCodeGoProtocolError, match="OpenCode Go") as error:
        llm.invoke("simulated malformed response")
    assert len(requests) == 1
    assert "sensitive-unknown-block" not in str(error.value)


@pytest.mark.unit
def test_go_messages_source_has_no_anthropic_sdk_import():
    """Wire compatibility cannot reintroduce an Anthropic client dependency."""
    import tradingagents.llm_clients.opencode_go_client as go_client
    import tradingagents.llm_clients.opencode_go_messages as go_messages

    imports = []
    for source in (go_client, go_messages):
        tree = ast.parse(Path(source.__file__).read_text(encoding="utf-8"))
        imports.extend(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        imports.extend(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )

    assert all(not name.startswith("anthropic") for name in imports)
    assert "tradingagents.llm_clients.anthropic_client" not in imports


@pytest.mark.unit
def test_minimax_m3_messages_uses_a_forced_schema_tool_for_structured_output(monkeypatch):
    """The one verified forced-tool model powers typed manager decisions on Go."""
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    def fake_go_gateway(request):
        requests.append(request)
        return httpx2.Response(
            200,
            request=request,
            json={
                "id": "msg_structured_simulated",
                "type": "message",
                "role": "assistant",
                "model": "minimax-m3",
                "stop_reason": "tool_use",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_structured",
                        "name": "_Decision",
                        "input": {"rating": "simulated"},
                    }
                ],
                "usage": {"input_tokens": 1, "output_tokens": 1},
            },
        )

    llm = OpenCodeGoClient(
        "minimax-m3",
        session_id="simulated-run",
        http_client=httpx2.Client(transport=httpx2.MockTransport(fake_go_gateway)),
    ).get_llm()

    assert llm.with_structured_output(_Decision).invoke("simulated manager request") == _Decision(
        rating="simulated"
    )
    body = json.loads(requests[0].content)
    assert body["tool_choice"] == {"type": "tool", "name": "_Decision"}
    assert body["tools"][0]["name"] == "_Decision"


@pytest.mark.unit
def test_qwen_messages_structured_binding_falls_back_without_a_forced_request(monkeypatch):
    """Qwen's verified named-tool 400 must be handled before it reaches Go."""
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []
    llm = OpenCodeGoClient(
        "qwen3.8-flash",
        session_id="simulated-run",
        http_client=httpx2.Client(
            transport=httpx2.MockTransport(
                lambda request: requests.append(request) or httpx2.Response(500, request=request)
            )
        ),
    ).get_llm()

    with pytest.raises(NotImplementedError, match="forced tool choice"):
        llm.with_structured_output(_Decision)
    assert bind_structured(llm, _Decision, "simulated manager") is None
    assert requests == []


@pytest.mark.unit
@pytest.mark.parametrize(
    ("model", "supports_structured"),
    [
        ("glm-5.3-flash", True),
        ("gpt-5.6-luna", True),
        ("minimax-m3", True),
        ("qwen3.8-flash", False),
    ],
)
def test_real_protocol_adapters_report_verified_structured_support_without_network(
    monkeypatch, model, supports_structured
):
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")

    llm = OpenCodeGoClient(model, session_id="simulated-run").get_llm()

    assert llm.bind_tools([]) is not None
    if supports_structured:
        assert llm.with_structured_output(_Decision) is not None
    else:
        with pytest.raises(NotImplementedError, match="forced tool choice"):
            llm.with_structured_output(_Decision)


@pytest.mark.unit
def test_graph_reuses_one_go_session_for_quick_and_deep_clients():
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = {"llm_provider": "opencode_go", "llm_max_retries": 8}

    first = graph._get_provider_kwargs()
    second = graph._get_provider_kwargs()

    assert first["opencode_go_session_id"]
    assert first["opencode_go_session_id"] == second["opencode_go_session_id"]
    assert "max_retries" not in first


@pytest.mark.unit
def test_every_ai_role_receives_the_selected_quick_or_deep_llm(monkeypatch):
    """Graph construction never selects a provider outside its two input LLMs."""
    import tradingagents.graph.setup as graph_setup
    from tradingagents.graph.conditional_logic import ConditionalLogic
    from tradingagents.graph.reflection import Reflector

    quick_llm = object()
    deep_llm = object()
    received: dict[str, object] = {}

    def record(name):
        def factory(llm):
            received[name] = llm
            return lambda state: state

        return factory

    for name in (
        "create_market_analyst",
        "create_sentiment_analyst",
        "create_news_analyst",
        "create_fundamentals_analyst",
        "create_bull_researcher",
        "create_bear_researcher",
        "create_research_manager",
        "create_trader",
        "create_aggressive_debator",
        "create_neutral_debator",
        "create_conservative_debator",
        "create_portfolio_manager",
    ):
        monkeypatch.setattr(graph_setup, name, record(name))
    monkeypatch.setattr(graph_setup, "create_msg_delete", lambda: lambda state: state)

    graph_setup.GraphSetup(
        quick_llm,
        deep_llm,
        {key: lambda state: state for key in ("market", "social", "news", "fundamentals")},
        ConditionalLogic(1, 1),
    ).setup_graph()

    quick_roles = {
        "create_market_analyst",
        "create_sentiment_analyst",
        "create_news_analyst",
        "create_fundamentals_analyst",
        "create_bull_researcher",
        "create_bear_researcher",
        "create_trader",
        "create_aggressive_debator",
        "create_neutral_debator",
        "create_conservative_debator",
    }
    assert {received[name] for name in quick_roles} == {quick_llm}
    assert received["create_research_manager"] is deep_llm
    assert received["create_portfolio_manager"] is deep_llm
    assert Reflector(quick_llm).quick_thinking_llm is quick_llm


@pytest.mark.unit
@pytest.mark.parametrize(
    ("status", "exception_type", "text"),
    [
        (401, OpenCodeGoAuthenticationError, "authentication"),
        (403, OpenCodeGoAuthenticationError, "authentication"),
        (429, OpenCodeGoQuotaError, "quota"),
    ],
)
def test_auth_and_quota_errors_are_redacted_and_do_not_name_a_fallback(
    status, exception_type, text
):
    error = classify_opencode_go_error(
        _FakeStatusError(status, "Bearer fake-go-key was rejected")
    )

    assert isinstance(error, exception_type)
    assert text in str(error).lower()
    assert "fake-go-key" not in str(error)
    assert "zen" not in str(error).lower()
    assert "openai" not in str(error).lower()


@pytest.mark.unit
def test_muse_region_restriction_is_a_terminal_availability_error(monkeypatch):
    """A model-specific 403 must not mislead users into rotating a valid Go key."""
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    def fake_go_gateway(request):
        requests.append(request)
        return httpx.Response(403, request=request, json={"error": {"message": "hidden"}})

    llm = OpenCodeGoClient(
        "muse-spark-1.3-contributor",
        session_id="simulated-run",
        http_client=httpx.Client(transport=httpx.MockTransport(fake_go_gateway)),
    ).get_llm()

    with pytest.raises(OpenCodeGoModelAvailabilityError, match="limited regions") as error:
        llm.invoke("simulated coding-agent request")

    assert error.value.is_terminal_provider_error is True
    assert "fake-go-key" not in str(error.value)
    assert len(requests) == 1
    assert str(requests[0].url) == f"{OPENCODE_GO_API_BASE_URL}/responses"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("model", "endpoint", "credential_header"),
    [
        ("glm-5.3-flash", "/chat/completions", "authorization"),
        ("gpt-5.6-luna", "/responses", "authorization"),
        ("qwen3.8-flash", "/messages", "x-api-key"),
    ],
)
@pytest.mark.parametrize(
    ("status", "exception_type"),
    [(401, OpenCodeGoAuthenticationError), (429, OpenCodeGoQuotaError)],
)
def test_simulated_protocol_errors_are_mapped_without_external_connections(
    monkeypatch, model, endpoint, credential_header, status, exception_type
):
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "fake-go-key")
    requests = []

    def fake_go_gateway(request):
        requests.append(request)
        response_cls = httpx2.Response if credential_header == "x-api-key" else httpx.Response
        return response_cls(status, request=request, json={"error": {"message": "hidden"}})

    transport_cls = httpx2.MockTransport if credential_header == "x-api-key" else httpx.MockTransport
    client_cls = httpx2.Client if credential_header == "x-api-key" else httpx.Client
    transport = transport_cls(fake_go_gateway)
    llm = OpenCodeGoClient(
        model,
        session_id="simulated-run",
        http_client=client_cls(transport=transport),
    ).get_llm()

    with pytest.raises(exception_type):
        llm.invoke("simulated provider request")

    assert len(requests) == 1
    assert str(requests[0].url) == f"{OPENCODE_GO_API_BASE_URL}{endpoint}"
    assert requests[0].headers["x-opencode-session"] == "simulated-run"
    assert requests[0].headers["user-agent"] == OPENCODE_GO_USER_AGENT
    if credential_header == "authorization":
        assert requests[0].headers[credential_header] == "Bearer fake-go-key"
    else:
        assert requests[0].headers[credential_header] == "fake-go-key"
