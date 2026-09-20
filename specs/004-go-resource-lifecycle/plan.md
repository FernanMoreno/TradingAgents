# Implementation Plan: OpenCode Go Transport Lifecycle

**Branch**: feature/opencode-go-provider | **Date**: 2026-09-20 | **Spec**:
[spec.md](spec.md)

## Summary

Add deterministic resource cleanup at the three ownership boundaries: the
direct Messages adapter owns its lazily-created HTTP client, the graph owns its
LLM instances, and the CLI owns its command graph. Preserve caller-injected
transports, library reuse, all provider routing, and error behavior.

## Technical Context

**Language/Version**: Python 3.10+

**Dependencies**: Existing HTTPX/LangChain/LangGraph; no new dependency

**Testing**: pytest with real local HTTPX clients and fakes only at the CLI
ownership seam

**Constraints**: No live provider/data call, fallback, new endpoint, broker,
or order execution

## Constitution Check

| Gate | Result |
|---|---|
| Explicit ownership | Pass: only owner closes its resource. |
| Compatibility | Pass: injected clients and reusable library graphs remain supported. |
| Test first | Pass: RED lifecycle tests precede production edits. |
| Error integrity | Pass: CLI `finally` closes without swallowing the original exception. |

## Source

    tradingagents/llm_clients/opencode_go_messages.py
    tradingagents/graph/trading_graph.py
    cli/main.py
    tests/test_opencode_go_provider.py
    tests/test_cli_*.py

## Implementation Phases

1. Write RED tests for adapter/graph/CLI ownership behavior.
2. Add narrow idempotent adapter and graph cleanup operations.
3. Invoke graph cleanup from the CLI's success/failure ownership boundary.
4. Run focused and full simulated tests, composition review, final diff review.

## Rollback

Revert the patch. No persistent data or remote resource is changed.
