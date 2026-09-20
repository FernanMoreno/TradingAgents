# Feature Specification: OpenCode Go Transport Lifecycle

**Feature Branch**: feature/opencode-go-provider

**Created**: 2026-09-20

**Status**: Complete

**Input**: Continue hardening OpenCode Go by correcting the confirmed lifecycle
gap: a direct Messages client that creates an owned pooled HTTP transport has
no supported graph-level shutdown path after a run.

## User Scenarios & Testing

### User Story 1 - Release Owned Go Connections (Priority: P1)

As a user who repeatedly runs TradingAgents in a long-lived process, I want a
completed Go-backed graph to release its internally owned HTTP connections, so
that reused processes do not accumulate idle connection pools.

**Independent Test**: Create real direct Messages clients with local-only
transports, close their owning graph, and verify that each owned client is
closed without sending HTTP.

**Acceptance Scenarios**:

1. **Given** a Go Messages client has created its own transport, **When** its
   graph is closed, **Then** the owned transport is closed.
2. **Given** close is called more than once, **When** the graph remains in
   memory, **Then** no error occurs and no additional transport is created.
3. **Given** a client was injected by its caller, **When** the adapter is
   closed, **Then** the caller-owned client remains open.

---

### User Story 2 - Close CLI-Owned Graphs (Priority: P2)

As a CLI user, I want the graph created for one completed command to be closed
even if that command raises, so that normal and failed CLI runs have the same
resource-cleanup behavior.

**Independent Test**: Exercise the CLI run ownership boundary with a closable
graph substitute and verify cleanup executes on completion and failure without
changing the analysis result or error.

**Acceptance Scenarios**:

1. **Given** the CLI finishes a run, **When** it returns its current result,
   **Then** it closes the graph it created afterwards.
2. **Given** the CLI run raises, **When** the error propagates, **Then** it
   still closes the graph once and preserves the original error.
3. **Given** a non-Go graph, **When** cleanup is requested, **Then** existing
   provider behavior remains unchanged.

### Edge Cases

- A Messages adapter with no constructed owned client must close harmlessly.
- Closing must never close an injected client.
- Deep and Quick LLM references may be the same object and must not be closed
  more than once.
- This correction adds no provider, fallback, endpoint, credential access,
  live analysis, broker, or order execution.

## Requirements

### Functional Requirements

- **FR-001**: The direct Go Messages adapter MUST provide an idempotent shutdown
  operation for its owned HTTP transport.
- **FR-002**: That operation MUST not close caller-injected transports.
- **FR-003**: A graph MUST expose an idempotent cleanup boundary that closes
  each unique owned LLM resource it holds.
- **FR-004**: The CLI ownership boundary MUST invoke graph cleanup in both
  successful and exceptional exits without suppressing the run result/error.
- **FR-005**: The correction MUST preserve existing Go protocol, timeout,
  session, tool, structured-output, and terminal-error behavior.
- **FR-006**: Tests MUST use local construction/fakes only and must not call
  OpenCode Go, another provider, financial services, brokers, or orders.

## Success Criteria

- **SC-001**: Every owned direct Messages client used by a closed graph reports
  a closed HTTP transport in simulated tests.
- **SC-002**: Cleanup is idempotent across repeated adapter/graph shutdown.
- **SC-003**: An injected transport remains open after adapter cleanup.
- **SC-004**: CLI success and failure coverage confirms cleanup exactly once
  while preserving the observable result/error.

## Assumptions

- The graph owns LLM instances it constructs and the CLI owns the graph it
  constructs for a command.
- Callers that construct a graph themselves retain the explicit cleanup option;
  the correction does not silently dispose a reusable graph during its run API.
- Existing non-Go LLM objects may not expose shutdown; cleanup must remain
  capability-based and harmless for them.
