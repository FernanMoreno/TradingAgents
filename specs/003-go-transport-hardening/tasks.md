# Tasks: Reliable OpenCode Go Transport Boundaries

**Input**: Design documents in specs/003-go-transport-hardening

**Tests**: Required. Each behavior change begins with a focused pytest
regression that is observed failing before production code changes.

## Phase 1: Regression Evidence

- [X] T001 Reproduce default unbounded direct Messages timeouts and the
  mixed-case Quick-preflight bypass with local constructor probes.
- [X] T002 [P] [US1] Add failing default-timeout and explicit-timeout/client
  preservation tests in tests/test_opencode_go_provider.py.
- [X] T003 [P] [US2] Add a failing mixed-case graph-preflight side-effect test
  in tests/test_opencode_go_provider.py.

## Phase 2: Boundary Corrections

- [X] T004 [US1] Remove the null timeout override only when constructing an
  owned direct transport in tradingagents/llm_clients/opencode_go_messages.py.
- [X] T005 [US2] Apply case-insensitive identity at the Go Quick preflight in
  tradingagents/graph/trading_graph.py.
- [X] T006 Run focused regressions in tests/test_opencode_go_provider.py.

## Phase 3: Composition and Validation

- [X] T007 Run static checks and simulated provider/client test gates with
  denied outbound proxy settings.
- [X] T008 Review transport, factory, catalog, graph, tool, structured-output,
  and terminal-error composition; record results in
  specs/003-go-transport-hardening/composition-review.md.
- [X] T009 Inspect the final diff, make graph-refresh and durable-knowledge
  decisions, and run verification-before-completion checks.

## Dependencies

T002 and T003 must show the intended RED failures before T004 and T005. T004
and T005 precede T006-T009. T002 and T003 are independently runnable; the two
production edits touch separate files.

## Implementation Strategy

Deliver the default-timeout correction and its regression first, then the
case-normalized preflight correction. Stop after both reported defects are
proven fixed; do not add lifecycle APIs, new configuration settings, providers,
or live requests.
