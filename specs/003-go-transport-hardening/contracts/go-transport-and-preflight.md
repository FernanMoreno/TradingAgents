# Contract: OpenCode Go Transport and Quick Preflight

## Direct Messages Transport

| Input | Expected behavior |
|---|---|
| No timeout and no injected client | Create an owned client with finite timeout phases. |
| Finite caller timeout | Create an owned client that uses that timeout. |
| Injected client | Return the injected client without constructing an owned one. |

## Quick Preflight

| Provider value | Known tool-incompatible Quick model | Result |
|---|---|---|
| `opencode_go` | Yes | Go configuration error before startup effects. |
| `OpenCode_Go` | Yes | The same Go configuration error before startup effects. |
| Non-Go provider | Any | Existing non-Go behavior. |

The preflight retains strict model and protocol routing: unknown Go identifiers
continue to be handled by the existing factory/client validation path.
