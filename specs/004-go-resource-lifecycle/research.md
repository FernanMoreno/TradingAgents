# Research: OpenCode Go Transport Lifecycle

## Evidence and Root Cause

`OpenCodeGoMessages` lazily creates an owned `httpx.Client` when no client is
injected. The adapter has no close operation, and `TradingAgentsGraph` retains
its Quick and Deep LLM objects without a general cleanup boundary. Therefore a
real request can leave pooled connections alive until garbage collection or
process exit. The graph already has explicit lifecycle handling for its
checkpointer, which establishes the local pattern for owned resources.

## Decision: Close at the resource owners

The adapter will close only its private owned client. The graph will close each
unique LLM only when it exposes a close operation. The CLI will own the graph
cleanup for the graph it creates. This preserves injected-client ownership and
library graph reuse semantics.

## Alternatives Rejected

- Rely on garbage collection: nondeterministic and unsuitable for repeated runs.
- Close every HTTP client from the adapter: violates caller ownership for
  injected transports.
- Close the graph automatically after every library run: breaks callers that
  deliberately reuse a graph.

## Knowledge Persistence Decision

Do not add a vault note. The owner/lifecycle contract is repository-specific
and will be preserved by this spec, tests, and implementation.
