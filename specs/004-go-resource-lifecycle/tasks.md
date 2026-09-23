# Tasks: OpenCode Go Transport Lifecycle

## Phase 1: Evidence

- [X] T001 Reproduce the absence of adapter/graph cleanup without a network request.
- [X] T002 [P] [US1] Add RED adapter and graph lifecycle tests in tests/test_opencode_go_provider.py.
- [X] T003 [P] [US2] Add RED CLI ownership-cleanup tests in the applicable tests/test_cli_*.py file.

## Phase 2: Correction

- [X] T004 [US1] Add idempotent owned-client cleanup in tradingagents/llm_clients/opencode_go_messages.py.
- [X] T005 [US1] Add unique closable-LLM cleanup in tradingagents/graph/trading_graph.py.
- [X] T006 [US2] Add CLI `finally` cleanup in cli/main.py.
- [X] T007 Run focused lifecycle regressions.

## Phase 3: Validation

- [X] T008 Run static/full simulated checks and document composition in specs/004-go-resource-lifecycle/composition-review.md.
- [X] T009 Review final diff, make graph/vault decisions, verify, commit, and push.
