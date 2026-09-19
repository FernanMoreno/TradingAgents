# Research: Capability-Safe OpenCode Go Quick Selection

## Decision: Use reviewed ordinary-tool capability as the Quick eligibility rule

**Rationale**: The market, news, and fundamentals analyst paths bind tools to
the Quick LLM before invocation. A direct Go Messages client explicitly
rejects binding when its model metadata reports no ordinary-tool support.
Therefore a Messages model without that support is known incompatible with the
Quick role. Chat Completions and Responses models retain their existing generic
tool-binding path.

**Alternatives considered**:

- Keep every model in Quick and fail at tool binding: rejected because an
  ordinary menu choice predictably fails after graph construction.
- Remove unsupported Messages models from all Go choices: rejected because the
  same models remain valid for free-text Deep roles.
- Filter only in the CLI: rejected because environment variables, preferences,
  and library configuration can bypass interactive selection.

## Decision: Validate known Go Quick incompatibility at graph construction

**Rationale**: The graph owns the conversion of selected configuration into
clients, tools, directories, and the workflow. A pure check at the beginning
of its constructor gives every configuration source the same safe failure
before client construction or other startup state changes.

**Alternatives considered**:

- Validate inside individual analysts: rejected because the graph would already
  have partially initialized and the error repeats in multiple roles.
- Validate inside the client factory: rejected because the factory does not
  know whether it is building a Quick or Deep role.
- Validate only saved preferences: rejected because callers may supply
  configuration directly.

## Decision: Preserve strict unknown-model handling

**Rationale**: Go maps each reviewed identifier to an incompatible wire
protocol. The existing strict client factory is the owner of errors for unknown
IDs. The new role check must ignore unknown IDs so that it does not obscure that
existing configuration error.

## Evidence and Root Cause

The shared catalog supplied every reviewed Go ID to both mode pickers. Six
Messages models have reviewed ordinary-tool capability set to false:
minimax-m2.7, minimax-m2.5, qwen3.8-max, qwen3.7-max, qwen3.7-plus, and
qwen3.6-plus. The direct Messages client raises before transport when tool
binding is requested, while three Quick analyst nodes invoke that binding.
The first incorrect boundary is the mode-agnostic catalog; graph preflight is
needed to cover callers that bypass the catalog.

## Knowledge Persistence Decision

Do not add a vault note. This is a bounded, repository-specific regression
whose durable rationale and executable contract live with this feature's Spec
Kit artifacts and tests. No new credential, account, or cross-project
operational knowledge was produced.
