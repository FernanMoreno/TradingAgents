# Implementation Plan: OpenCode Go Messages Token Default

**Branch**: `feature/opencode-go-provider` | **Date**: 2026-09-20 | **Spec**:
[spec.md](spec.md)

## Summary

Correct the direct Go Messages payload boundary so it always supplies a
protocol-specific finite `max_tokens` value. Preserve the existing global
configuration as the explicit override and leave all other protocol adapters
unchanged.

## Technical Context

**Language/Version**: Python 3.10+

**Dependencies**: Existing HTTPX and LangChain; no new dependency

**Testing**: pytest with in-process HTTPX `MockTransport`; no external calls

**Constraints**: No model-name policy, fallback, catalog refresh, new endpoint,
credential access, financial analysis, broker, or order execution

## Constitution Check

| Gate | Result |
|---|---|
| Narrow ownership | Pass: the direct Messages adapter owns its payload shape. |
| Configuration precedence | Pass: existing explicit `max_tokens` remains authoritative. |
| Compatibility | Pass: no global default or non-Messages behavior changes. |
| Test first | Pass: RED payload regressions precede the production edit. |
| Error integrity | Pass: no error classifier or provider route is changed. |

## Source

    tradingagents/llm_clients/opencode_go_messages.py
    tradingagents/llm_clients/opencode_go_client.py
    tradingagents/graph/trading_graph.py
    tests/test_opencode_go_provider.py
    tests/test_llm_max_tokens.py

## Implementation Phases

1. Write RED local-transport assertions for default and explicit Messages limits.
2. Add the smallest protocol-level payload default in the direct Messages adapter.
3. Run focused, full simulated, static, and composition checks.

## Rollback

Revert the patch. It changes no stored data, remote resource, model catalog, or
user configuration.
