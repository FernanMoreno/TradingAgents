# Composition Review: Reliable OpenCode Go Transport Boundaries

**Date**: 2026-09-20

## Changed Subsystems

- Direct OpenCode Go Messages transport construction.
- OpenCode Go Quick-role configuration preflight.
- Simulated Go provider regression coverage.

## Impact Surface and Neighbors Reviewed

Graphify extraction over the Python source and tests identified
`TradingAgentsGraph`, `OpenCodeGoClient`, `OpenCodeGoMessages`,
`create_llm_client`, and `test_opencode_go_provider.py` as connected hubs. The
source confirms these paths:

1. Graph configuration reaches Go Quick preflight before `set_config`, directory
   creation, client construction, tool-node construction, and workflow setup.
2. The factory normalizes provider case, constructs `OpenCodeGoClient`, and the
   reviewed model protocol selects the direct Messages adapter only where
   appropriate.
3. The Messages adapter obtains its injected or owned HTTP client, posts only to
   the Go Messages endpoint, and routes status failures to the Go error
   classifier.
4. Tool binding and structured output remain inside the same adapter; agent
   helpers preserve terminal Go authentication/quota errors rather than falling
   back to a different provider.

## Boundaries and Invariants Checked

| Boundary | Invariant | Evidence |
|---|---|---|
| Configuration → preflight | Every accepted Go casing rejects known tool-incompatible Quick models before side effects. | 12 parametrized graph-preflight cases pass. |
| Factory → client | Factory and preflight use the same lowercase Go identity. | Source inspection plus mixed-case regression. |
| Client → transport | No supplied timeout uses finite HTTPX defaults; finite supplied timeout remains unchanged. | Eight default-transport cases and explicit-timeout regression pass. |
| Injected client → adapter | Injected simulated transport remains the client owner. | Existing direct Go protocol tests pass with `MockTransport`. |
| Transport → errors | Auth/quota errors remain terminal and redacted; no fallback provider is selected. | Existing provider error regressions pass. |
| Graph → roles/tools/structured output | Quick/Deep instances remain the only LLMs distributed through analysts, debates, managers, risk, reflection, and final processing. | Existing all-role, tool, and structured-output regressions pass. |

## Architecture and Composition Checks

- `ruff check .` and Python compilation passed.
- `project-composition-check` is not applicable: `.ai/project-name` is absent.
- No Import Linter, dependency-cruiser, or equivalent architecture configuration
  is present; Ruff is the available static gate.
- The full simulated suite passed: `1012 passed, 2 skipped, 22 warnings, 116
  subtests passed`. The skips are the missing optional Bedrock dependency and a
  DeepSeek test explicitly gated as live without a real credential.
- The initial full-suite attempt intentionally used an invalid DeepSeek value;
  it activated that live-gated test and the local proxy blocked it. Root cause
  was test gating, not this patch. The final suite uses `placeholder`, preserving
  the test's no-live-call contract.

## Contract and Dependency Assessment

No provider HTTP request shape, endpoint, authentication header, external
service contract, persistence schema, event, queue, or database changed. The
corrections execute before an owned transport sends a request, and existing
in-process `MockTransport` tests exercise the direct adapter's contract;
Testcontainers and Pact are therefore not applicable.

## Residual Risks

- This repair intentionally restores the HTTP dependency's finite default; no
  live Go latency test was run, so an operator requiring a longer deadline must
  continue to supply a finite explicit timeout through the supported client
  kwargs.
- The existing direct adapter retains an owned pooled HTTP client without a
  graph-level close lifecycle. A long-lived host that repeatedly constructs
  graphs after real calls could retain connections. That independent audit
  finding is not changed by this two-bug repair.
- A non-terminal network timeout in a structured agent can still follow the
  established same-provider free-text retry path; it cannot select Zen or a
  different provider. This behavior predates the fix and is not a quota or
  authentication fallback.

## Verdict

**PASS WITH RISKS** — the two requested root causes are corrected and the
changed boundaries pass simulated composition coverage. The listed lifecycle,
live-latency, and same-provider timeout-retry questions remain explicitly out
of scope.

## Independent Code Review

A read-only review of the final working-tree diff found no critical, important,
or minor issue. It confirmed that timeout omission preserves explicit and
injected-client behavior, and that mixed-case Go preflight still precedes all
startup effects.
