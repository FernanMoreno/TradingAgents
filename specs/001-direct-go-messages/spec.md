# Feature Specification: Direct OpenCode Go Messages

**Feature Branch**: `feature/opencode-go-provider`

**Created**: 2026-09-19

**Status**: Implemented

**Input**: Replace the OpenCode Go Messages transport with a direct OpenCode Go
adapter that has no Anthropic SDK dependency and represents model-specific tool
and structured-output capabilities.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use Go Without an Anthropic Client (Priority: P1)

As a TradingAgents user who selects an OpenCode Go Messages model, I want every
model request to be made directly to OpenCode Go so that selecting Go never
depends on or routes through Anthropic.

**Why this priority**: Provider ownership is the core user requirement and
must be true for ordinary analysis, tool calls, and final responses.

**Independent Test**: Select a supported Messages model with a simulated
transport and verify its request reaches only the documented Go host with Go
credentials, session identity, and user-agent.

**Acceptance Scenarios**:

1. **Given** a configured Go Messages model, **When** an agent asks for a
   response, **Then** the request is sent only to the documented OpenCode Go
   Messages endpoint.
2. **Given** the same model, **When** the request completes, **Then** its text
   and tool-call result can continue through the existing TradingAgents graph.
3. **Given** another configured provider, **When** it is selected, **Then** its
   existing behavior remains unchanged.

---

### User Story 2 - Use Only Capabilities the Chosen Model Supports (Priority: P2)

As a user selecting a Go Messages model, I want TradingAgents to use tools and
structured results only when that model supports the required behavior, so that
the workflow does not spend a failed request on an unsupported forced action.

**Why this priority**: Models on the same endpoint have different behavior;
safe handling preserves the workflow and protects included usage.

**Independent Test**: Exercise models with known supported and unsupported
forced-tool behavior through controlled responses and verify the correct path
is chosen before a request is made.

**Acceptance Scenarios**:

1. **Given** a model verified to support a forced schema tool, **When** a
   structured-result role runs, **Then** it receives a validated result.
2. **Given** a model not verified to support a forced schema tool, **When** a
   structured-result role runs, **Then** it uses the established free-text
   path without first making a failing forced-tool request.
3. **Given** a normal agent tool, **When** the chosen model returns a tool
   request, **Then** TradingAgents receives the tool name, arguments, and call
   identifier needed to execute it.

---

### User Story 3 - Receive Clear, Safe Failure Behavior (Priority: P3)

As a user of Go, I want authentication, quota, protocol, and unsupported-model
failures to stop clearly within Go so that no hidden provider or paid fallback
is used.

**Why this priority**: Honest failure handling protects credentials, usage, and
the user's provider choice.

**Independent Test**: Simulate credential, quota, malformed-response, and
unsupported-capability cases and confirm the exposed error is clear, redacted,
and never invokes another provider.

**Acceptance Scenarios**:

1. **Given** missing or rejected Go credentials, **When** a request is built
   or sent, **Then** the user receives a redacted Go-specific error.
2. **Given** a Go quota response, **When** it occurs, **Then** the run stops
   after that request without retrying or changing provider.
3. **Given** an unrecognized Messages response, **When** it is received,
   **Then** the error identifies the Go protocol problem without revealing a
   secret.

### Edge Cases

- A Go Messages model produces thinking blocks before text or a tool request.
- A model supports ordinary tools but rejects selection of one named tool.
- A tool result must be included in a later Go Messages request.
- A model identifier is listed by Go but has not yet been capability-tested.
- The user provides a custom backend URL, another provider credential, or a
  malformed Go response.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST keep `opencode_go` as an explicit provider and
  send every selected Go Messages request only to the documented Go endpoint.
- **FR-002**: The system MUST not construct or use an Anthropic SDK client for
  any `opencode_go` Messages request.
- **FR-003**: The system MUST preserve the existing workflow's text responses,
  tool routing, selected-provider propagation, session identity, and final
  result processing.
- **FR-004**: The system MUST represent forced-tool and structured-result
  capability separately for each Go Messages model and use only verified
  capabilities.
- **FR-005**: The system MUST preserve the existing free-text fallback for a
  structured-result role whose selected model cannot guarantee that result.
- **FR-006**: The system MUST stop on Go authentication or quota failures with
  redacted errors and MUST NOT retry, switch provider, use Zen balance, or use
  another paid API.
- **FR-007**: The system MUST reject unconfigured Go model identifiers and
  custom Go backend URLs before a network request is created.
- **FR-008**: The system MUST preserve all existing non-Go providers and MUST
  not add brokerage or order-execution behavior.

### Key Entities

- **Go model capability**: The reviewed behavior a specific Go model exposes
  for normal tools, forced schema tools, and structured results.
- **Go Messages response**: A Go response containing text, thinking, tool
  request, completion reason, and usage information.
- **Go session identity**: The stable non-secret conversation identifier sent
  with requests belonging to one TradingAgents graph run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of simulated Go Messages requests use the documented Go
  host and no simulated request reaches an Anthropic host or client.
- **SC-002**: 100% of tested Messages models use only their explicitly
  verified forced-tool behavior; no test sends a known-unsupported forced tool.
- **SC-003**: All existing provider-selection and graph-role tests continue to
  pass with the Go provider selected.
- **SC-004**: Authentication and quota scenarios end after one Go request with
  a redacted user-visible error and zero fallback requests.

## Assumptions

- The official Go endpoint and Messages model table remain the authoritative
  source for routing; its compatible wire format does not make Anthropic the
  selected provider.
- The tested behavior currently establishes forced-tool support for
  `minimax-m3` and lack of it for `qwen3.8-flash`; other Messages models remain
  conservative until independently verified.
- A free-text fallback remains a valid original-flow outcome where a typed
  structured result cannot be guaranteed.
- Real provider validation stays limited to the previously authorized minimal,
  non-financial smoke tests; the implementation test suite uses simulated
  transports.
