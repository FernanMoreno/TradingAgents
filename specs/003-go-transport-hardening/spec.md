# Feature Specification: Reliable OpenCode Go Transport Boundaries

**Feature Branch**: feature/opencode-go-provider

**Created**: 2026-09-20

**Status**: Implemented

**Input**: Correct the two audited OpenCode Go regressions: a direct Messages
request can have no HTTP deadline, and a valid case variation of the provider
name can bypass the safe Quick-role preflight.

## User Scenarios & Testing

### User Story 1 - Stop a Stalled Go Messages Request (Priority: P1)

As a TradingAgents user running a Messages-protocol OpenCode Go model, I want
each request to have a finite HTTP deadline by default, so that an unavailable
or stalled service cannot leave the complete workflow waiting indefinitely.

**Why this priority**: The same direct transport is used by any role configured
with a Messages model, including the final processing path. An infinite wait
prevents a clear terminal provider error from reaching the user.

**Independent Test**: Construct a real Messages client without a caller-supplied
timeout and verify that all of its HTTP timeout phases are finite, without
sending a request.

**Acceptance Scenarios**:

1. **Given** a Messages Go model without an explicit timeout, **When** it first
   constructs its HTTP transport, **Then** connection, read, write, and pool
   waits are finite.
2. **Given** a caller supplies a finite timeout, **When** the transport is
   constructed, **Then** that caller choice remains in effect.
3. **Given** a caller injects an HTTP client for a simulated test or controlled
   host, **When** the model runs, **Then** it continues to use that client.

---

### User Story 2 - Apply the Quick Safety Check to Equivalent Provider Names (Priority: P2)

As a library user who configures the provider outside the interactive CLI, I
want the Go Quick-role safety check to recognize accepted case variations of
the provider name, so that an invalid Quick model is rejected before graph
initialization regardless of how the name was cased.

**Why this priority**: The catalog and client factory already accept a
case-insensitive provider identifier. A preflight that treats the same input
differently can permit startup side effects before the expected clear error.

**Independent Test**: Construct a graph with `OpenCode_Go` and a reviewed
tool-incompatible Quick model; prove it raises the Go configuration error before
configuration, directory, or AI-client startup work.

**Acceptance Scenarios**:

1. **Given** an accepted mixed-case OpenCode Go provider identifier and a
   known tool-incompatible Quick model, **When** graph construction begins,
   **Then** it stops at the same preflight boundary as the canonical spelling.
2. **Given** that invalid configuration, **When** it is rejected, **Then** no
   provider client, fallback, Zen service, data tool, directory, or network
   operation has started.
3. **Given** a non-Go provider identifier or a valid Go Quick model, **When**
   graph construction begins, **Then** the existing provider behavior remains
   unchanged.

### Edge Cases

- An absent timeout must receive a finite default; a finite caller-supplied
  timeout must not be overwritten.
- An injected client must remain the transport owner and must not be replaced.
- A non-string or unrelated provider value must not be interpreted as Go.
- This correction does not add a client-close lifecycle API, new provider,
  model, network endpoint, financial analysis, broker, or order execution.

## Requirements

### Functional Requirements

- **FR-001**: A direct OpenCode Go Messages client without an explicit timeout
  MUST use finite HTTP limits for connection, read, write, and pool waits.
- **FR-002**: A caller-supplied finite timeout and an injected HTTP client MUST
  retain their established behavior.
- **FR-003**: Every provider comparison controlling Go Quick-role validation
  MUST use the same case-insensitive identity rule as the supported factory and
  catalog entry points.
- **FR-004**: A known Go Quick model lacking ordinary tools MUST fail before
  configuration mutation, directory creation, client construction, data tools,
  fallback selection, or network activity for every accepted casing.
- **FR-005**: The correction MUST preserve the current strict Go model,
  protocol, session, credential, and terminal-error behavior.
- **FR-006**: Tests MUST be simulated and MUST not call OpenCode Go, another
  AI provider, market-data services, brokers, or order execution.

### Key Entities

- **Messages transport deadline**: The finite limits used by a direct OpenCode
  Go Messages HTTP client when the caller did not supply a timeout.
- **Provider identity**: The normalized provider value used by catalog, factory,
  graph preflight, and Go-specific configuration behavior.
- **Quick preflight**: The pure compatibility check that runs before graph
  initialization for a known Go Quick model.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All eight reviewed Messages models construct transports with zero
  unbounded timeout phases under the default configuration.
- **SC-002**: A mixed-case accepted Go provider with each known incompatible
  Quick model performs zero startup side effects before its configuration error.
- **SC-003**: Focused Go provider regressions complete with zero external HTTP
  requests and zero fallback-provider constructions.
- **SC-004**: Existing Go provider tests remain green after both regressions are
  corrected.

## Assumptions

- The transport library's documented default timeout is an appropriate finite
  baseline where TradingAgents does not expose a dedicated Go timeout setting.
- Existing client injection is a deliberate testing/embedding seam and remains
  supported.
- Provider spelling is already intentionally case-insensitive at the public
  catalog and factory boundaries, so preflight must match that contract.
