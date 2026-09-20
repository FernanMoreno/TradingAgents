# Data Model: Go Transport and Provider Identity

## Messages Transport Inputs

| Field | Meaning | Invariant |
|---|---|---|
| Caller timeout | Optional finite HTTP timing choice | Preserved when supplied. |
| Injected client | Caller-owned transport seam | Used instead of creating an owned client. |
| Default timeout | Dependency finite default | Used when neither input provides timing. |

## Provider Identity Inputs

| Value | Meaning | Invariant |
|---|---|---|
| `opencode_go` | Canonical Go provider name | Enables Go-specific Quick validation. |
| Accepted case variation | Same provider identity | Receives identical preflight behavior. |
| Other or non-string value | Not OpenCode Go | Does not enter Go Quick validation. |

## Invariants

- The transport correction makes no request while a client is constructed.
- The Quick preflight is pure and runs before graph initialization effects.
- No fallback provider or endpoint is selected by either correction.
