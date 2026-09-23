# Composition Review: Capability-Safe OpenCode Go Quick Selection

**Date**: 2026-09-20

**Verdict**: PASS WITH DOCUMENTED TEST-SUITE WARNINGS

## Changed Subsystems

- Reviewed OpenCode Go model capability metadata
- Shared provider/mode model catalog used by the CLI and preference sanitizer
- TradingAgents graph initialization lifecycle
- Go provider regression coverage and operator documentation
- Two pre-existing data-test fixtures corrected to avoid accidental Yahoo
  reachability and timezone-sensitive cache mtimes

## Neighbors Reviewed

| Boundary | Evidence and invariant |
|---|---|
| Go catalog to CLI picker | Both pickers consume the same mode-specific catalog. Quick excludes only Messages IDs without ordinary tools; Deep retains all reviewed IDs. |
| Saved preferences to catalog | Preference sanitization uses the shared options for each role, so an obsolete Go Quick choice is discarded while an allowed Deep choice survives. |
| Graph configuration to startup side effects | Validation executes before shared dataflow configuration, directory creation, client construction, memory, tools, and graph setup. |
| Graph Quick LLM to analysts | Market, news, and fundamentals analysts bind tools before invocation; the preflight prevents a known unsupported Messages client from reaching those paths. |
| Graph to Go factory/client | Valid selections continue to factory construction. Unknown IDs pass through the new predicate so the strict Go client still owns unknown-model/protocol errors. |
| Go provider to other providers | The preflight is gated on the explicit Go provider and does not change factory behavior, credentials, endpoints, retries, Zen, or non-Go catalogs. |

## Contracts and Failure Propagation

- The checked capability is ordinary tool support, not forced-tool or structured
  support; existing MiniMax and Qwen handling is unchanged.
- A rejected configuration raises the existing terminal Go configuration error,
  identifying the invalid Quick field and model without credentials.
- Rejection has no retry, fallback, provider switch, network request, data
  request, cache update, directory creation, or partial graph setup.
- Deep availability is intentionally independent of Quick eligibility.
- There is no state migration, event, queue, cache schema, transaction, lock,
  cancellation, or API-version change in this patch.

## Checks Run

| Check | Result |
|---|---|
| Red regression proof | Three focused tests failed before implementation: Quick catalog contained all six, preference restoration retained one, and graph changed shared config before failure. |
| Focused Go preflight proof | 8 passed: all six incompatible models reject before side effects, plus catalog and preference behavior. |
| Go/provider/CLI/model regression | 73 passed, 113 subtests passed. |
| Data-test isolation regressions | 10 passed with HTTP/HTTPS blocked. |
| Full isolated suite | 997 passed, 2 skipped, 22 existing warnings, and 116 subtests passed with fake credentials and outbound HTTP/HTTPS blocked. |
| Ruff, compileall, diff whitespace | Passed after the final six-model parameterization. |
| Architecture checker | No Import Linter/dependency-cruiser configuration is present. The configured static architecture-adjacent gate is Ruff. |
| Project composition command | Not runnable: this repository has no .ai/project-name, although the command is installed. |
| Pact/independent-provider contract test | Not applicable: this patch does not add or change an independently deployed HTTP/message contract; Go transport contracts already use in-process simulated responses. |

## Real Dependencies

No real AI, OpenCode, Zen, market-data, broker, or order-execution dependency
was used. Tests used fake credentials and a local nonexistent HTTP/HTTPS proxy.
The existing empty-Yahoo test fixture now mocks the reachability decision, so it
does not leak a real financial-service connection during the suite.

## Warnings and Residual Risks

- The full suite has existing runtime warnings for intentionally unknown
  provider-model test cases and divide-by-zero memory fixtures; they are not
  introduced by this change.
- Two expected skips remain when the optional langchain_aws dependency is not
  installed and when the live DeepSeek test has only a placeholder key.
- Chat Completions and Responses models continue to rely on their existing
  generic tool binding. This patch makes no new claim about their capabilities.
- Real Go calls remain outside this verification pass by design; earlier
  authorized neutral protocol probes are not repeated here.
