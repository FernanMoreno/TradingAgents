# Feature Specification: Capability-Safe OpenCode Go Quick Selection

**Feature Branch**: feature/opencode-go-provider

**Created**: 2026-09-20

**Status**: Implemented

**Input**: Correct the discovered mismatch where the quick-thinking selector
offers OpenCode Go Messages models that cannot perform the analyst tool calls
required by the unchanged TradingAgents workflow.

## User Scenarios & Testing

### User Story 1 - Select a Quick Model That Can Run Analysts (Priority: P1)

As a TradingAgents user selecting OpenCode Go, I want the quick-thinking model
menu to contain only models that can complete the tool-enabled analyst roles,
so that my selected run does not fail at its first analyst before work begins.

**Why this priority**: Quick-thinking models are used by tool-enabled analyst
roles. Offering a known-incompatible model makes a normal menu selection
nonfunctional.

**Independent Test**: Inspect the Quick and Deep selections for Go and verify
that every Go Messages model without ordinary tools is absent from Quick yet
remains available for Deep.

**Acceptance Scenarios**:

1. **Given** the user selects OpenCode Go, **When** Quick options are shown,
   **Then** a Go Messages model without ordinary tools is not offered.
2. **Given** the same user selects Deep options, **When** the Deep menu is
   shown, **Then** all reviewed Go model identifiers remain available,
   including Messages models that only support free-text work.
3. **Given** a reviewed Go model that supports ordinary tools, **When** Quick
   options are shown, **Then** the model remains selectable.

---

### User Story 2 - Fail Safely for Noninteractive Configuration (Priority: P2)

As a user who supplies configuration through environment variables, saved
preferences, or library code, I want an incompatible Go quick-thinking model
to fail clearly before a graph starts, so that a stale setting cannot trigger
data collection, an AI request, or a provider change.

**Why this priority**: Noninteractive configuration bypasses the menu and can
retain identifiers that were previously offered.

**Independent Test**: Construct a graph with a known tool-incompatible Go
Messages quick model and prove it raises a Go-specific configuration error
before it creates an AI client or any graph side effect.

**Acceptance Scenarios**:

1. **Given** a noninteractive Go configuration with a Messages model that
   lacks ordinary tools as its quick model, **When** graph construction begins,
   **Then** construction stops with a clear explanation of the required
   capability.
2. **Given** that configuration failure, **When** it is raised, **Then** no
   AI client, data tool, network request, fallback provider, Zen use, or
   financial analysis is started.
3. **Given** an unknown Go model identifier, **When** graph construction
   begins, **Then** the established strict model-validation error remains the
   source of the failure.

---

### User Story 3 - Preserve the Existing Provider and Deep Flow (Priority: P3)

As a current TradingAgents user, I want this guard to leave valid Go selections
and all non-Go providers unchanged, so that fixing the Quick selection does not
alter the original workflow or introduce another provider.

**Independent Test**: Exercise the shared catalog, preference sanitization,
and graph preflight with valid Go and non-Go inputs, using simulated clients
only.

**Acceptance Scenarios**:

1. **Given** a valid Go Quick model and any reviewed Go Deep model, **When**
   the graph is created, **Then** the existing provider-specific construction
   path remains available.
2. **Given** a saved preference with an incompatible Go Quick model, **When**
   preferences are sanitized, **Then** the stale Quick selection is removed
   while its valid Deep selection is retained.
3. **Given** another provider, **When** its model selections are used,
   **Then** its catalog and graph construction behavior remain unchanged.

### Edge Cases

- A saved Quick selection names a Go Messages model that has no ordinary tool
  support while Deep uses the same model.
- A valid Go Quick model is paired with a free-text-only Go Deep model.
- A Go identifier is not in the reviewed catalog.
- A user has no Go API key; capability validation must not read, display, or
  require it.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST derive Go Quick eligibility from reviewed model
  capabilities rather than treating every Go model as interchangeable.
- **FR-002**: The Quick selection MUST exclude every reviewed Go Messages model
  known not to support ordinary tools.
- **FR-003**: The Deep selection MUST retain every reviewed Go model in the
  strict Go catalog.
- **FR-004**: The system MUST reject a known-incompatible Go Quick model
  supplied outside the selector before creating an AI client, data tool,
  directory side effect, or network operation.
- **FR-005**: That rejection MUST identify the configured model and explain
  that the Quick role requires ordinary tools, without exposing credentials or
  proposing a provider, endpoint, Zen, or paid fallback.
- **FR-006**: Unknown Go identifiers MUST continue to use the established
  strict provider-model validation path.
- **FR-007**: Valid Go Quick/Deep choices and all non-Go provider behavior
  MUST remain compatible with the current workflow.
- **FR-008**: The change MUST use simulated tests only; it MUST not invoke Go,
  another AI provider, market-data services, brokers, or order execution.

### Key Entities

- **Go model capability**: The reviewed ordinary-tool support associated with
  one strict OpenCode Go model identifier.
- **Thinking role**: The user-selected Quick or Deep use of a model in one
  TradingAgents graph.
- **Go Quick preflight**: The validation that compares the configured Quick
  model with the tool requirement before graph initialization.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The Quick Go option set contains zero of the six reviewed
  Messages models without ordinary-tool support, while Deep contains all six.
- **SC-002**: A programmatic configuration using each of those six models as
  Quick fails with zero AI-client construction attempts and zero requests.
- **SC-003**: A valid Go Quick choice and a non-Go selection preserve their
  existing construction path in 100% of simulated coverage scenarios.
- **SC-004**: The relevant Go provider, catalog, preference, and graph tests
  complete without contacting an external AI or financial service.

## Assumptions

- The existing model metadata remains the authority for which direct Messages
  models support ordinary tools; this correction does not infer new support.
- Quick roles require ordinary tools because the market, news, and fundamentals
  analyst paths bind tools before they run; Deep roles continue to support
  free-text processing.
- The six reviewed Messages models without ordinary tools are valid Go model
  identifiers for Deep work and must not be globally removed.
