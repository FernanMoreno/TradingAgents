# Implementation Plan: Direct OpenCode Go Messages

**Branch**: `feature/opencode-go-provider` | **Date**: 2026-09-19 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from `specs/001-direct-go-messages/spec.md`

## Summary

Replace the Go Messages path's dependency on the Anthropic Python SDK with a
first-party TradingAgents adapter that sends the documented Messages wire format
directly to OpenCode Go. Preserve the existing `opencode_go` provider factory,
model selector, graph session propagation, tool lifecycle, and no-fallback
errors. Represent forced tool selection and typed structured output per model:
only `minimax-m3` is currently verified for forced tools; `qwen3.8-flash` uses
ordinary tools but must select the existing free-text structured-result fallback
before it would send a known-invalid forced tool request.

## Technical Context

**Language/Version**: Python `>=3.10` (project target; test environment uses
the repository virtual environment)

**Primary Dependencies**: `langchain-core`, `langchain-openai`,
`langchain-anthropic` for the independent existing Anthropic provider, `httpx`
as a direct dependency for the new Go Messages transport, Pydantic, pytest

**Storage**: N/A; the client stores no credentials, messages, or session state
outside the graph-run session identifier already owned by `TradingAgentsGraph`.

**Testing**: pytest with in-process `httpx.MockTransport`; targeted real Go
checks remain optional and limited to prior explicit authorization.

**Target Platform**: Python CLI/library on Windows and supported project
platforms.

**Project Type**: Python application and CLI with LangGraph orchestration.

**Performance Goals**: One outbound request per normal Go invocation and one
request for an auth/quota failure; no automatic provider or balance fallback.

**Constraints**: Fixed OpenCode Go host; `OPENCODE_GO_API_KEY` only; stable
`x-opencode-session`; truthful Go user agent; no broker/order behavior; no
secret in source, diagnostics, or tests.

**Scale/Scope**: One new direct Messages adapter, capability metadata, existing
factory integration, simulated protocol contracts, and documentation. It does
not change non-Go providers or the TradingAgents graph topology.

## Constitution Check

| Principle | Gate | Result |
|---|---|---|
| Preserve the Agent Workflow | Keep factory, graph, tools, and final paths stable. | Pass: adapter is substitutable at the existing Messages branch. |
| Explicit Provider Ownership | No Anthropic SDK or external host in Go Messages path. | Pass: fixed Go URL and direct transport are planned. |
| Test-First Evidence | Add failing contracts before production code. | Pass: tests are the first implementation task. |
| Compatibility-Safe Protocol Changes | Preserve non-Go clients and model-specific behavior. | Pass: existing Anthropic provider remains untouched; capability defaults are conservative. |
| Composition Before Completion | Exercise graph/session/tool/error boundaries. | Pass: composition scenarios and review are required. |

No constitution exception is requested.

## Project Structure

### Documentation (this feature)

```text
specs/001-direct-go-messages/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── go-messages-adapter.md
├── quickstart.md
└── tasks.md
```

### Source Code

```text
tradingagents/
├── llm_clients/
│   ├── factory.py
│   ├── opencode_go_client.py
│   ├── opencode_go_messages.py
│   └── opencode_go_models.py
├── graph/
│   └── trading_graph.py
└── agents/utils/
    └── structured.py

tests/
└── test_opencode_go_provider.py
```

**Structure Decision**: Add a focused Go-only Messages module rather than
changing the existing native `anthropic_client.py`. The factory still returns
`OpenCodeGoClient`; only its Messages branch returns the direct adapter.

## Implementation Phases

1. Add failing simulated contracts for direct Messages construction, exact Go
   request routing, message conversion, tool-result round trips, model-specific
   forced tool behavior, malformed payloads, and no Anthropic imports.
2. Add model capability metadata with conservative defaults and a direct
   LangChain chat model implementing synchronous generation and tool binding.
3. Replace only the Messages branch of `OpenCodeGoClient`; retain Chat
   Completions and Responses adapters unchanged.
4. Update test doubles and documentation; run targeted, regression, static,
   composition, and final verification gates.

## Migration and Rollback

**Forward path**: Existing configuration (`llm_provider=opencode_go`, model
ID, API key, session settings) remains unchanged. On selecting a Messages model,
the factory builds the direct Go adapter instead of the Anthropic SDK adapter.

**Compatibility window**: Chat Completions and Responses Go models retain their
existing OpenAI-compatible adapter. The independent `anthropic` provider and
its dependency remain available unchanged.

**Rollback**: Revert the adapter and capability metadata commit; users need no
configuration or data migration. No persistent data is transformed.

**Partial failure**: The direct adapter maps 401/403/429 through the existing
redacted Go error classification and treats invalid protocol shapes as Go
protocol errors. It never retries quota responses or constructs another
provider.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Custom Messages adapter | Go documents a Messages endpoint, while the existing client is tied to an Anthropic SDK. | Reusing that SDK preserves an unwanted dependency and hides model-specific behavior. |
