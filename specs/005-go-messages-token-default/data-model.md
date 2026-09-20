# Data Model: OpenCode Go Messages Token Default

## Request-policy values

| Value | Owner | Rule |
|---|---|---|
| `max_tokens` | Existing graph/client configuration | When supplied, send its exact validated value. |
| `4096` | Direct Go Messages adapter | Send only when `max_tokens` is absent. |

There is no persistent state, migration, schema storage, or model-catalog
change.
