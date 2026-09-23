# Contract: OpenCode Go Transport Lifecycle

| Operation | Owned transport | Injected transport | Repeated operation |
|---|---|---|---|
| Adapter close | Closes it | Leaves it open | No error; no second close. |
| Graph close | Closes unique closable LLMs | Delegates without violating injection owner | No error. |
| CLI exit | Closes its graph in `finally` | Preserves result/error | Runs once. |
