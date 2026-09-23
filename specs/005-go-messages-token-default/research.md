# Research: OpenCode Go Messages Token Default

## Decision: Default at the protocol boundary

Use one Messages-adapter default rather than a per-model table entry.

**Rationale**: The observed failure was the absence of a field in the Go
Messages request. Applying the policy at that transport allows current and
future reviewed Messages models to inherit it, while preserving the distinct
Chat Completions and Responses paths.

**Alternatives considered**:

- Per-Qwen model metadata: rejected because removal, renaming, or addition of a
  Messages model would require a catalogue policy edit despite identical wire
  behavior.
- Global `DEFAULT_CONFIG["max_tokens"]`: rejected because it would alter every
  provider's existing opt-in configuration behavior.
- Runtime catalogue refresh: rejected as unrelated extra network work that does
  not make a retired model available.

## Decision: Default value and override

Use `8192` when `max_tokens` is absent and preserve any explicit value.

**Rationale**: Live, non-financial probes established that Qwen Go Messages
rejects a request when the field is absent and accepts a request when it is
present. The 64-token probe was diagnostic only; 8192 is selected as a useful
bounded application default and remains user-overridable through the existing
configuration path.

**Residual verification**: a real, non-financial Go Messages smoke with 8192
can verify gateway acceptance after implementation; it must never be a market
or broker operation.
