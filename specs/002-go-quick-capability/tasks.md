# Tasks: Capability-Safe OpenCode Go Quick Selection

**Input**: Design documents in specs/002-go-quick-capability

**Tests**: Required. Each behavior change begins with a focused pytest
regression that is observed failing before production code changes.

## Phase 1: Regression Evidence

- [X] T001 Reproduce the mode-agnostic Go picker and direct Messages
  tool-binding failure using tests/test_opencode_go_provider.py.
- [X] T002 Add failing Quick/Deep catalog and preference-sanitization
  regression tests in tests/test_opencode_go_provider.py and
  tests/test_cli_prefs.py.
- [X] T003 Add a failing graph-preflight regression that proves no AI client or
  startup side effect occurs for a known incompatible Go Quick model in
  tests/test_opencode_go_provider.py.

## Phase 2: Capability Boundary

- [X] T004 Add dependency-free Go role-eligibility helpers in
  tradingagents/llm_clients/opencode_go_models.py.
- [X] T005 Populate Quick and Deep Go options through the role-aware helper in
  tradingagents/llm_clients/model_catalog.py.
- [X] T006 Invoke the Go Quick preflight before all constructor side effects in
  tradingagents/graph/trading_graph.py.
- [X] T007 Pass focused catalog, preference, and graph-preflight regressions.

## Phase 3: Documentation and Validation

- [X] T008 Update user-facing Go model guidance in README.md.
- [X] T009 Run the focused Go/CLI/model tests and full project tests without
  external AI or financial calls.
- [X] T010 Run project static/architecture gates, review composition across
  catalog, preferences, graph, factory, client, and analysts, and document
  results in specs/002-go-quick-capability/composition-review.md.
- [X] T011 Inspect the final diff, make the graph-refresh and durable-knowledge
  decisions, and run final verification-before-completion checks.

## Dependencies

T001-T003 must finish and show the intended RED failures before T004-T006.
T004 precedes T005 and T006. T007 precedes T008-T011.

## Implementation Strategy

Deliver the role predicate and Quick catalog first, then the graph preflight
that covers noninteractive callers. Stop after the narrow regression is proven;
do not add new providers, model capabilities, external calls, or workflow
features.
