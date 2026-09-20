# Data Model: Go Transport Ownership

| Resource | Owner | Cleanup rule |
|---|---|---|
| Adapter-created HTTP client | `OpenCodeGoMessages` | Close once; allow a later lazy recreation. |
| Injected HTTP client | Caller | Never close from adapter or graph. |
| Quick/Deep LLM object | `TradingAgentsGraph` | Close each unique closable object once. |
| Command graph | CLI command boundary | Close on success and failure. |

## Invariants

- Cleanup is idempotent.
- Cleanup sends no request and never selects a different provider.
- Closing a resource does not redact, replace, or suppress an existing run error.
