# Composition Review: Direct OpenCode Go Messages

**Date:** 2026-09-19
**Verdict:** PASS WITH RISKS

## Changed subsystems

- Go model metadata and factory protocol dispatch.
- Direct `httpx` Messages LangChain chat model.
- Structured-output fallback error propagation.
- Configuration/documentation and simulated provider contracts.

## Boundaries and invariants checked

| Boundary | Invariant and evidence |
|---|---|
| Factory -> provider | `opencode_go` selects `OpenCodeGoClient`, which selects the fixed direct Messages URL for Messages models. The native Anthropic factory branch remains separate. |
| Graph -> LLM roles | Existing graph propagation contract proves every analyst, debate, manager, risk, reflection, and final role receives only quick/deep LLM instances selected by the graph. |
| LLM -> ToolNode -> LLM | Simulated tool calls become standard `AIMessage.tool_calls`; system prompts, assistant tool uses, one or multiple consecutive `ToolMessage` results, and thinking blocks round-trip through Messages in order. |
| Structured binding -> fallback | `minimax-m3` uses a named schema tool and Pydantic parser. `qwen3.8-flash` rejects structured binding before transport, so the existing plain Go free-text path is selected. |
| Structured invocation -> error | Go authentication, quota, and protocol errors carry `is_terminal_provider_error`; the shared helper re-raises them and makes no plain-text retry. |
| Configuration -> transport | Key, stable session, strict model catalog, and fixed endpoint are validated before transport. A custom backend is rejected before client construction. |
| HTTP -> caller | Simulated 401/403/429 map to redacted errors. A malformed response produces one terminal protocol error, with no response value reflected in the message. |

## Architecture and composition evidence

- Final Graphify code graph: 15 files, 189 nodes, 311 edges, 11 communities.
  Extracted calls include `create_llm_client -> OpenCodeGoClient ->
  OpenCodeGoMessages` and `with_structured_output -> bind_tools`; no Go Messages
  call/import edge reaches `AnthropicClient`.
- No project-specific import-linter or architecture dependency checker is
  configured. `project-composition-check` could not run because
  `.ai/project-name` is absent.
- Simulated composition coverage runs in-process HTTP transports rather than
  billable provider integrations. This is sufficient for exact headers,
  endpoint, payload, ordering, parser, error, and no-fallback contracts.
- One separately authorized direct non-financial smoke request to `minimax-m3`
  returned `OK` through the new adapter. It did not use market data or tools.

## Review feedback resolved

Independent review found and the final contracts now cover:

1. consecutive parallel tool results grouping into one user Messages turn;
2. non-forced `auto`/`any` tool choice separate from named forcing; and
3. malformed response errors that do not interpolate remote data.

The follow-up review found no Critical or Important issues.

## Residual risks

- Tool/structured capabilities are deliberately verified only for
  `minimax-m3` and `qwen3.8-flash`; other Messages models accept direct text
  transport but remain conservative until capability evidence is added.
- Project callers use synchronous LLM invocation. LangChain's default async
  bridge was not exercised against the live Go service.
- Availability, subscription limits, and OpenCode account-level “Use balance”
  configuration remain external to this repository. The code never changes
  endpoint, provider, model, or API key; users who do not want account-level
  Zen continuation must disable that console setting.
