# Tasks: Direct OpenCode Go Messages

**Input**: Design documents from `specs/001-direct-go-messages/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, and
contracts/go-messages-adapter.md

**Tests**: Required. Every behavior change uses a focused pytest contract that
must fail before production implementation.

## Phase 1: Setup

**Purpose**: Keep generated agent artifacts out of version control and make the
direct transport dependency explicit.

- [X] T001 Add `.agents/` to `.gitignore` while retaining tracked Spec Kit
  project artifacts in `.specify/` and `specs/`.
- [X] T002 Add the direct `httpx` runtime dependency in `pyproject.toml`.

---

## Phase 2: Foundational Contracts

**Purpose**: Establish a capability data model and test helpers that all user
stories require.

- [X] T003 Add failing capability and direct-Messages transport contracts in
  `tests/test_opencode_go_provider.py`.
- [X] T004 Add failing request/response conversion and tool-result round-trip
  contracts in `tests/test_opencode_go_provider.py`.
- [X] T005 Add failing no-Anthropic-import and no-external-host contracts in
  `tests/test_opencode_go_provider.py`.
- [X] T006 Run the focused pytest selection and record the expected red failure
  before creating `tradingagents/llm_clients/opencode_go_messages.py`.

---

## Phase 3: User Story 1 - Direct Go Messages Ownership (Priority: P1) 🎯 MVP

**Goal**: Use the documented Go Messages endpoint without an Anthropic client
while preserving the existing client factory and LangChain tool lifecycle.

**Independent Test**: A mocked Go response proves the factory returns the
direct adapter, makes one request only to Go, and maps text plus tool calls into
the existing message contract.

- [X] T007 [US1] Create the direct synchronous Go Messages chat model in
  `tradingagents/llm_clients/opencode_go_messages.py`.
- [X] T008 [US1] Replace only the Messages branch in
  `tradingagents/llm_clients/opencode_go_client.py` and remove Go-path
  Anthropic imports/classes.
- [X] T009 [US1] Pass the direct-Go factory, endpoint, response, tool, and
  no-import contracts in `tests/test_opencode_go_provider.py`.

**Checkpoint**: A selected Messages model uses direct Go transport; Chat
Completions, Responses, and the separately selected Anthropic provider remain
unchanged.

---

## Phase 4: User Story 2 - Capability-Safe Tools and Structured Results (Priority: P2)

**Goal**: Bind only verified forced schema tools and avoid predictable Qwen
forced-tool failures while preserving the graph's free-text fallback.

**Independent Test**: Mocked MiniMax returns typed structured output; mocked
Qwen binds ordinary tools but refuses structured binding before transport.

- [X] T010 [US2] Add per-model tool and structured-result metadata in
  `tradingagents/llm_clients/opencode_go_models.py`.
- [X] T011 [US2] Implement capability-aware `bind_tools` and
  `with_structured_output` behavior in
  `tradingagents/llm_clients/opencode_go_messages.py`.
- [X] T012 [US2] Add and pass MiniMax forced-schema, Qwen no-forced-schema,
  and tool-result round-trip contracts in `tests/test_opencode_go_provider.py`.
- [X] T013 [US2] Verify `tradingagents/agents/utils/structured.py` uses its
  existing free-text path for a Qwen-like unsupported structured binding, with
  coverage in `tests/test_opencode_go_provider.py` or its focused helper test.

**Checkpoint**: Known unsupported forcing makes zero outbound requests and all
fallback generation remains on Go.

---

## Phase 5: User Story 3 - Safe Failure and Compatibility (Priority: P3)

**Goal**: Keep Go auth, quota, malformed-response, and configuration failures
clear and terminal without affecting other providers.

**Independent Test**: Simulated 401/403/429 and invalid response shapes prove
redaction, one-request behavior, and no fallback.

- [X] T014 [US3] Add direct-transport auth, quota, malformed response, and
  invalid tool-input tests in `tests/test_opencode_go_provider.py`.
- [X] T015 [US3] Implement redacted protocol-error handling in
  `tradingagents/llm_clients/opencode_go_messages.py` and reuse the existing
  Go auth/quota classification in `tradingagents/llm_clients/opencode_go_client.py`.
- [X] T016 [US3] Verify existing Go key, custom backend rejection, session, and
  graph-role propagation tests remain passing in `tests/test_opencode_go_provider.py`.

---

## Phase 6: Polish and Cross-Cutting Validation

- [X] T017 Update Go-specific dependency and capability documentation in
  `README.md` and `.env.example`.
- [X] T018 Run targeted tests, full pytest under UTC, Ruff, `git diff --check`,
  and applicable architecture/composition checks.
- [X] T019 Perform composition review across factory, graph session, Messages
  adapter, tool routing, structured fallback, configuration, and error paths.
- [X] T020 Refresh Graphify impact evidence or document why the source graph
  has no structural change beyond the new direct adapter.
- [X] T021 Inspect the final diff, persist only the durable provider decision if
  explicitly selected, and complete verification-before-completion.

## Dependencies & Execution Order

- T001–T002 prepare the repository and declared transport dependency.
- T003–T006 are the mandatory red phase and block implementation.
- T007–T009 deliver the P1 direct transport MVP.
- T010–T013 depend on P1 and deliver capability-safe tools/structure.
- T014–T016 depend on the adapter and complete error compatibility.
- T017–T021 run only after all implementation tests pass.

## Implementation Strategy

1. Reach a red test proving that Go Messages is currently backed by an
   Anthropic class and that a direct model is absent.
2. Implement the narrow direct adapter until the P1 contracts pass.
3. Add capabilities one model at a time; never generalize observed behavior.
4. Run composition and regression gates before committing or pushing.
