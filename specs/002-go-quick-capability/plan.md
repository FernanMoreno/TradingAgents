# Implementation Plan: Capability-Safe OpenCode Go Quick Selection

**Branch**: feature/opencode-go-provider | **Date**: 2026-09-20 | **Spec**:
[spec.md](spec.md)

## Summary

Correct the Go model-selection boundary at the narrowest responsible layer.
The shared Go catalog will distinguish eligibility for the tool-enabled Quick
role from availability for the free-text-compatible Deep role. Graph
construction will validate only known Go Quick models before it mutates
interface state, creates directories, builds an AI client, or initializes
data/tool nodes. Unknown model IDs retain the existing factory validation
behavior. No endpoint, credential, provider routing, model capability, or
graph topology changes.

## Technical Context

**Language/Version**: Python 3.10 or newer

**Primary Dependencies**: Existing LangChain/LangGraph project dependencies;
no dependency addition

**Storage**: Existing in-memory configuration and remembered CLI preferences;
no schema or persistence migration

**Testing**: pytest with constructor-level fakes and no external HTTP

**Target Platform**: Windows CLI/library plus existing supported platforms

**Project Type**: Python application and command-line interface

**Performance Goals**: Invalid known Go Quick configuration fails before one
client-construction attempt or externally observable initialization side effect

**Constraints**: Preserve strict Go model IDs; never guess tool support; never
select a fallback provider, Zen, or another paid API; no financial live run,
broker, or order execution

**Scale/Scope**: One capability predicate, mode-aware catalog population,
preflight at graph ownership boundary, focused regression tests, and Go
documentation update

## Constitution Check

| Principle | Gate | Result |
|---|---|---|
| Explicit provider ownership | The correction cannot build a secondary provider. | Pass: validation runs before factory construction. |
| Capability truthfulness | Do not infer untested tool support. | Pass: reuse existing reviewed metadata only. |
| Test-first evidence | Reproduce before behavior changes. | Pass: focused RED tests precede production edits. |
| Compatibility | Deep and non-Go flows must remain stable. | Pass: filter only the Go Quick view and preflight only known incompatible Go IDs. |
| Safe state lifecycle | Invalid configuration leaves no partial graph state. | Pass: preflight precedes interface config and directories. |

No constitution exception is requested.

## Project Structure

### Documentation

    specs/002-go-quick-capability/
    ├── spec.md
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── contracts/go-role-eligibility.md
    ├── quickstart.md
    ├── tasks.md
    └── composition-review.md

### Source

    tradingagents/llm_clients/opencode_go_models.py
    tradingagents/llm_clients/model_catalog.py
    tradingagents/graph/trading_graph.py
    tests/test_opencode_go_provider.py

## Implementation Phases

1. Write focused regression tests for the Quick/Deep catalog split and
   graph-construction failure before any AI client or initialization side
   effect.
2. Add a dependency-free role-eligibility predicate to the existing reviewed
   Go model metadata, filtering only Quick options.
3. Apply the predicate at the graph's configuration ownership boundary before
   all initialization actions.
4. Update operator documentation, run focused and full regression checks, and
   review cross-subsystem behavior.

## Migration and Rollback

**Forward path**: Existing valid Go settings require no change. Saved or
environment-supplied Quick settings that choose one of six reviewed
tool-incompatible Messages models are rejected at startup with a clear error.
The corresponding Deep settings remain valid.

**Compatibility window**: No stored format changes. Preference sanitization
automatically drops a stale invalid Quick value because it already consumes the
shared mode-specific catalog.

**Rollback**: Revert this patch. No files, credentials, model settings, or
remote resources are transformed.

**Partial failure**: Validation is pure and precedes side effects. It makes no
network call and cannot cause a fallback provider to run.

## Complexity Tracking

| Choice | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Mode-aware catalog plus graph preflight | The menu and noninteractive configuration are separate entry points. | Filtering only the menu leaves environment and library callers broken. |
| Keep incompatible models in Deep | Deep roles use free-text processing and model IDs remain valid. | Removing them globally narrows supported Go functionality without evidence. |
| Leave unknown IDs to current factory | Strict Go protocol mapping already owns unknown-ID errors. | A new earlier error would duplicate or change established validation behavior. |
