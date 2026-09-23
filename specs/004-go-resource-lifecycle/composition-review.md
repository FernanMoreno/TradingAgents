# Composition Review: OpenCode Go Transport Lifecycle

**Date**: 2026-09-20

## Changed Subsystems

- The direct OpenCode Go Messages adapter's ownership of its lazy HTTPX client.
- `TradingAgentsGraph` lifecycle management for the Quick and Deep LLMs it
  constructs.
- The CLI command's success and exceptional cleanup boundary.
- Simulated lifecycle regressions for the adapter, graph, and CLI.

## Impact Surface and Neighbors Reviewed

A final code-only Graphify extraction over the six changed source/test files
found 270 nodes, 428 directed edges, and 9 communities. It identifies
`run_analysis`, `TradingAgentsGraph`, `OpenCodeGoMessages`, their close paths,
and their regression tests as the relevant connected components. Source review
confirms the actual ownership route:

1. The CLI constructs one `TradingAgentsGraph` for a command.
2. The graph constructs and distributes its Quick and Deep LLMs across
   analysts, debates, managers, risk, reflection, and final processing.
3. A direct Go Messages LLM creates an HTTPX client only on first request.
4. CLI completion invokes graph cleanup; graph cleanup ends any checkpoint and
   closes every distinct closable LLM; the Go adapter closes only its private
   HTTPX client.

## Boundaries and Invariants Checked

| Boundary | Invariant | Evidence |
|---|---|---|
| Adapter -> HTTPX | A private client is closed once and the adapter remains reusable/idempotent. | Direct local-client regression passes. |
| Caller injection -> adapter | A caller-supplied HTTP client remains open. | `MockTransport` regression passes. |
| Graph -> LLMs | Quick and Deep references can be identical and are closed once; missing `close` remains harmless. | Shared-LLM and strict repeated-close regressions pass. |
| Graph -> checkpoint | Checkpoint cleanup cannot prevent attempts to close all LLMs. | `close()` records cleanup errors only after attempting every resource; checkpoint lifecycle suite passes. |
| CLI -> graph | Command-owned graphs close after setup, `Live` entry/body, success, and stream failure. | Pre-stream and stream-failure lifecycle regressions pass. |
| CLI error propagation | A cleanup failure after a stream failure is logged without replacing the stream error; a cleanup failure after success stays visible. | Dedicated failure-order regression passes and source has separate exceptional/success paths. |
| Provider compatibility | No endpoint, protocol, session, tool, structured-output, authentication, quota, or fallback behavior changes. | Existing Go-provider tests and full simulated suite pass. |

## Architecture and Composition Checks

- `ruff check` on changed Python files, `compileall`, and `git diff --check`
  passed.
- No Import Linter, dependency-cruiser, or equivalent architecture configuration
  exists in this repository; Ruff is the available static gate.
- `project-composition-check` is not applicable: this repository has no
  `.ai/project-name`.
- Focused affected-suite check passed: **101 passed**.
- Full simulated suite passed: **1021 passed, 2 skipped, 22 warnings, 116
  subtests passed**. The skips are the missing optional Bedrock dependency and
  the intentionally credential-gated DeepSeek live test. The warnings predate
  this change and concern unknown-model tests and a synthetic divide-by-zero
  data fixture.

## Contract and Dependency Assessment

No external wire contract changed. The added tests construct local HTTPX
clients or use in-process fakes; they make no provider, market-data, broker, or
order request. A disposable real external dependency, Testcontainers, and Pact
are not applicable because this patch neither changes a remotely deployed
consumer/provider protocol nor persists shared state.

## Residual Risks

- No real OpenCode Go request was run for this lifecycle-only correction, so a
  production server's connection-close timing remains unverified by design.
- `TradingAgentsGraph.close()` is an explicit lifecycle operation for
  programmatic callers; an explicitly closed graph should not be reused for a
  new analysis. Construct a fresh graph for a new lifecycle.
- The existing graph API has no concurrent-use/close guarantee. This patch does
  not add locking or cancellation semantics.

## Verdict

**PASS WITH RISKS** — ownership, idempotency, exceptional cleanup, and error
integrity are covered through the CLI-to-graph-to-adapter boundary without
altering Go routing or contacting any external provider.

## Independent Code Review

The final read-only review found no unresolved critical or important issue. It
confirmed cleanup coverage for setup, `Live` entry/body, stream failure, and
successful completion, along with graph-level idempotency and best-effort
closure of independent LLM resources.
