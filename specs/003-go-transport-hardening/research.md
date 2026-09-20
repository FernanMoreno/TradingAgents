# Research: Reliable OpenCode Go Transport Boundaries

## Decision: Preserve the HTTP library's finite default when no timeout is supplied

**Rationale**: Passing an explicit null timeout to the direct Messages client
disables every HTTP timeout phase. Constructing the client without that override
uses the dependency's finite default instead. This is the narrowest correction:
it adds no guessed Go-specific duration and preserves finite caller-provided
values.

**Alternatives considered**:

- Add a new Go-specific timeout configuration setting: rejected because the
  requested repair needs no new surface and the existing client already accepts
  a caller timeout.
- Hard-code a new long duration: rejected because no reviewed provider contract
  establishes one and it would alter behavior beyond removing the accidental
  unbounded override.
- Leave the null override: rejected because an unavailable gateway can hold the
  workflow indefinitely.

## Decision: Normalize at the graph preflight boundary

**Rationale**: The factory, catalog, and provider-specific graph kwargs already
lowercase the provider identity. The Quick preflight is the first inconsistent
boundary. Applying the same normalization in that guard makes invalid accepted
spellings fail before any graph startup work.

**Alternatives considered**:

- Require callers to use lowercase: rejected because the public factory and
  catalog already accept the mixed-case value.
- Normalize configuration globally at construction: rejected because it changes
  stored/shared configuration beyond this guard.
- Move validation later to the factory: rejected because the factory lacks the
  Quick-versus-Deep role and startup side effects would already have occurred.

## Evidence and Root Cause

- The direct Messages adapter stores `None` as its timeout default and passes it
  directly to its owned HTTP client. The dependency interprets that as no
  timeout for connect, read, write, and pool phases.
- The factory and catalog lower the provider name. The Go Quick preflight uses
  an exact string comparison, therefore `OpenCode_Go` passes factory/catalog
  routing but skips the preflight.
- Constructor-level local probes reproduce both conditions without an HTTP
  request or a credential.

## Knowledge Persistence Decision

Do not add a vault note. The provider-specific root causes, constraints, and
executable contracts are maintained in this feature's repository artifacts and
tests; no cross-project operational knowledge was produced.
