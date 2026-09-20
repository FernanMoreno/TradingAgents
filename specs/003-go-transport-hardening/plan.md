# Implementation Plan: Reliable OpenCode Go Transport Boundaries

**Branch**: feature/opencode-go-provider | **Date**: 2026-09-20 | **Spec**:
[spec.md](spec.md)

## Summary

Correct the two first incorrect boundaries found in the Go audit. The direct
Messages transport must not pass a null timeout that disables dependency
defaults. The graph Quick preflight must compare provider identity using the
same case-insensitive rule already used by catalog, factory, and Go-specific
kwargs. Both corrections are narrow, preserve injected/explicit client options,
and require no new provider, endpoint, model capability, or API call.

## Technical Context

**Language/Version**: Python 3.10 or newer

**Primary Dependencies**: Existing HTTPX, LangChain, and LangGraph dependencies;
no dependency addition

**Storage**: Existing in-memory configuration; no schema or persistence change

**Testing**: pytest with real constructors, simulated credentials, and in-process
HTTP transports only

**Target Platform**: Windows CLI/library plus existing supported platforms

**Project Type**: Python application and command-line interface

**Performance Goals**: Default direct Messages construction has four finite
timeout phases; mixed-case invalid Go Quick configuration has zero startup
side effects

**Constraints**: No external AI/financial call, fallback, Zen, broker, or order
execution; preserve explicit finite timeouts and injected test clients

**Scale/Scope**: Two narrow production conditions and focused regression tests

## Constitution Check

| Principle | Gate | Result |
|---|---|---|
| Explicit provider ownership | No fallback or secondary provider may be constructed. | Pass: both changes are local guards. |
| Transport safety | A missing timeout must not mean unbounded wait. | Pass: rely on existing dependency finite default. |
| Configuration consistency | Accepted provider spellings must behave identically. | Pass: normalize only at the inconsistent guard. |
| Test-first evidence | Reproduce before behavior changes. | Pass: focused RED tests precede production edits. |
| Compatibility | Explicit timeout and injected clients remain unchanged. | Pass: test both seams. |

No constitution exception is requested.

## Project Structure

### Documentation

    specs/003-go-transport-hardening/
    ├── spec.md
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── contracts/go-transport-and-preflight.md
    ├── quickstart.md
    ├── tasks.md
    └── composition-review.md

### Source

    tradingagents/llm_clients/opencode_go_messages.py
    tradingagents/graph/trading_graph.py
    tests/test_opencode_go_provider.py

## Implementation Phases

1. Add isolated RED tests for default finite timeout, explicit timeout/client
   preservation, and mixed-case preflight before startup effects.
2. Remove only the null timeout override from direct owned-client construction.
3. Normalize only the Quick preflight provider comparison.
4. Run focused and full simulated tests, inspect cross-boundary composition,
   review the final diff, and verify without a real credential.

## Migration and Rollback

**Forward path**: Default Messages calls receive a finite deadline. Existing
finite timeouts and injected clients remain valid. Equivalent Go provider
spellings now reject invalid Quick models at the same safe boundary.

**Compatibility window**: No setting, data, credential, or model identifier is
transformed. The prior accidental no-timeout behavior is not retained.

**Rollback**: Revert the patch. No remote resource, persisted setting, or user
data changes require compensation.

**Partial failure**: Both conditions are evaluated before a transport request.
They cannot route a request to a fallback provider.

## Complexity Tracking

| Choice | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Reuse dependency default timing | Removes the accidental unbounded override without inventing a new provider policy. | A new hard-coded timeout changes more behavior than needed. |
| Local preflight normalization | Matches current public case-insensitive routing. | Global config rewrite could alter unrelated shared state. |
