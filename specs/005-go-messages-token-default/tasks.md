# Tasks: OpenCode Go Messages Token Default

## Phase 1: Evidence

- [X] T001 Reproduce the omitted default in a local simulated Messages request in tests/test_opencode_go_provider.py.
- [X] T002 [US1] Add RED protocol-level default payload regressions in tests/test_opencode_go_provider.py.
- [X] T003 [US2] Add a RED explicit-override payload regression in tests/test_opencode_go_provider.py.

## Phase 2: Correction

- [X] T004 [US1] Add the default only in tradingagents/llm_clients/opencode_go_messages.py.
- [X] T005 [US2] Preserve the existing `max_tokens` passthrough in tradingagents/llm_clients/opencode_go_client.py without a global-config change.

## Phase 3: Validation

- [X] T006 Run focused simulated payload and max-token regressions.
- [X] T007 Run static/full simulated checks and record composition in specs/005-go-messages-token-default/composition-review.md.
- [X] T008 Review the final diff, make the durable-knowledge decision, verify, commit, and push.
- [X] T009 Raise the bounded Messages fallback to `8192`, prove its request
  shape with local fakes and reviewed Go models, and update the contract.
