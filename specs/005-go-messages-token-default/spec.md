# Feature Specification: OpenCode Go Messages Token Default

**Feature Branch**: `feature/opencode-go-provider`

**Created**: 2026-09-20

**Status**: Complete

**Input**: Make every OpenCode Go Messages request include a safe output-token
limit when no caller limit is configured, without coupling the behavior to
individual model names or changing other providers.

## User Scenarios & Testing

### User Story 1 - Run a Messages Model Without a Global Limit (Priority: P1)

As a TradingAgents user selecting an OpenCode Go Messages model, I want a
normal run to send the required output-token field even when I did not set a
global limit, so that a compatible Go model does not fail solely because that
field is absent.

**Independent Test**: Construct a Messages LLM with a local-only HTTP
transport and no configured limit, invoke it, and verify that its request body
contains the documented Go-specific default.

**Acceptance Scenarios**:

1. **Given** a Go Messages client has no explicit output-token limit, **When**
   it sends a request, **Then** the request includes a finite default of 8192.
2. **Given** the client selects a different Go Messages model, **When** it
   sends a request, **Then** it receives the same protocol-level behavior
   without a model-name branch.

### User Story 2 - Preserve an Explicit User Limit (Priority: P2)

As a user who configured `max_tokens`, I want TradingAgents to send exactly my
chosen limit, so that the Go safety default does not override deliberate output
or consumption control.

**Independent Test**: Construct a Messages LLM with an explicit limit and
verify that the local-only request contains that value rather than the default.

**Acceptance Scenarios**:

1. **Given** a Go Messages client receives an explicit positive limit, **When**
   it sends a request, **Then** the request contains that exact value.
2. **Given** a standard API provider or a Go Chat/Responses model, **When** no
   global limit is configured, **Then** this feature adds no new parameter to
   its request path.

## Edge Cases

- The existing global `max_tokens` setting remains opt-in and retains its
  existing validation and precedence.
- The correction must not access credentials, OpenCode CLI files, model
  catalog endpoints, financial data, brokers, or order execution.
- A removed or unauthorized model remains an explicit provider availability or
  authentication failure; this feature must not select another model/provider.

## Requirements

### Functional Requirements

- **FR-001**: Every request produced by the direct OpenCode Go Messages
  adapter MUST include `max_tokens`.
- **FR-002**: The adapter MUST use `8192` only when no explicit client limit
  is present.
- **FR-003**: An explicit `max_tokens` value passed through existing
  TradingAgents configuration MUST take precedence over the Go default.
- **FR-004**: The default MUST be selected by the Messages protocol boundary,
  not a list of individual model identifiers.
- **FR-005**: Chat Completions, Responses, and non-Go provider behavior MUST
  remain unchanged when no global limit is set.
- **FR-006**: Tests MUST use simulated local HTTP transports and make no
  external provider, market-data, broker, or order requests.

## Success Criteria

- **SC-001**: Simulated no-limit Qwen and MiniMax Messages requests both carry
  `max_tokens: 8192`.
- **SC-002**: A simulated explicit limit reaches the Messages request body
  unchanged.
- **SC-003**: Existing no-global-limit behavior for other providers remains
  covered by the nearest regression suite.
- **SC-004**: The focused Go-provider suite and full simulated suite complete
  without failures introduced by the correction.

## Assumptions

- `8192` is a bounded, useful Go Messages fallback; it is not inferred from
  the 64-token connectivity probe, which only established that the field must
  be present.
- Users needing a larger or smaller cap use the existing `max_tokens` setting.
- OpenCode Go may retire models; protocol-level request construction avoids a
  special code path for each active model but cannot make a retired model
  available.
