# Composition Review: OpenCode Go Messages Token Default

**Date**: 2026-09-20

## Changed Subsystems

- The direct OpenCode Go Messages adapter's JSON request construction.
- Local HTTP-transport regressions for default and explicit output limits.
- The Spec Kit contract, plan, and validation record for this compatibility
  correction.

## Impact Surface and Neighbors Reviewed

A code-only Graphify extraction over the affected request/configuration/test
surface found 223 nodes, 426 edges, and 19 communities. It identified
`TradingAgentsGraph._get_provider_kwargs`, `OpenCodeGoClient._base_kwargs`,
`OpenCodeGoClient.get_llm`, and `OpenCodeGoMessages._payload` as the relevant
route. Source review verified the route:

1. Graph configuration forwards `max_tokens` only when the user explicitly
   configured it.
2. The Go client preserves that value unchanged and routes reviewed Messages
   models to the direct adapter.
3. The direct adapter now supplies `4096` only when that forwarded value is
   absent, immediately before its Go HTTP request.
4. Chat Completions, Responses, tool binding, structured output, terminal
   errors, session identity, and model catalogue selection do not cross this
   changed branch.

## Boundaries and Invariants Checked

| Boundary | Invariant | Evidence |
|---|---|---|
| Global config -> graph | Unset `max_tokens` remains absent from generic provider kwargs. | Existing `test_llm_max_tokens.py` coverage passed in the focused suite. |
| Graph -> Go client | An explicit validated user value remains the value passed to the adapter. | Local request regression sends `777`. |
| Go client -> Messages adapter | Every reviewed Messages model reaches the same protocol-level default, not a model-specific branch. | Local Qwen/MiniMax regressions and real eight-model smoke passed. |
| Messages adapter -> Go HTTP | A no-limit request includes `max_tokens: 4096`. | In-process `MockTransport` assertions and real Go Messages responses passed. |
| Adapter -> other providers/protocols | No global configuration or Chat/Responses request shape changes. | Source route review plus 1025-test full suite passed. |
| Error and retry behavior | No fallback, auth/quota classifier, retry, session, or endpoint change. | Direct diff/source review and existing Go-provider regressions passed. |

State, persistence, transactions, events, cache invalidation, concurrency, and
migrations are not involved: the correction is a pure per-request payload
default and writes no shared state.

## Architecture and Composition Checks

- `ruff check tradingagents/llm_clients/opencode_go_messages.py
  tests/test_opencode_go_provider.py` passed.
- `python -m compileall` for the changed Python files passed.
- `git diff --check` passed.
- No Import Linter or equivalent architecture checker is configured.
- `project-composition-check` is not applicable because this repository has no
  `.ai/project-name`.

## Composition and Integration Scenarios

- RED test: no-limit Qwen and MiniMax Messages payloads failed with the expected
  missing `max_tokens` key before the production edit; an explicit value already
  passed.
- GREEN test: local Qwen/MiniMax default and explicit override scenarios passed.
- Focused simulated suite: **97 passed**.
- Configuration forwarding regression: **24 passed**, including the existing
  `opencode_go` path with an explicit `max_tokens` value.
- Final full simulated suite: **1025 passed, 2 skipped, 22 warnings, 116 subtests
  passed**. All provider keys were process-overridden with placeholders; the
  only credential-gated DeepSeek integration test was skipped.
- Real non-financial Go smoke: all eight reviewed Messages models returned the
  fixed connectivity marker with the default left unset in client construction.
  The probe used no tools, market data, broker, order, or fallback.

## Contract and Dependency Assessment

The changed HTTP request field is covered locally with an in-process HTTPX
transport and then exercised against the selected official Go endpoint. Pact is
not applicable because TradingAgents has no separately deployed provider it
controls. Testcontainers is not applicable because no database, queue, cache,
or other disposable infrastructure participates in this payload-only contract.

## Review and Residual Risks

- An independent read-only review found no critical or important issue. Its
  one coverage observation — verification of configuration-to-Go forwarding —
  was addressed before the final full suite.
- `4096` is an intentional finite fallback, so exceptionally long responses may
  be truncated. Users can set the existing `max_tokens` configuration to their
  required limit.
- Model retirement or regional availability remains an OpenCode service
  condition and still stops explicitly without a fallback.
- A full financial analysis was deliberately not run.

## Verdict

**PASS WITH RISKS** — the configuration-to-adapter contract, local request
shape, explicit override, all simulated provider paths, and every current Go
Messages model have been validated without provider fallback or market activity.
