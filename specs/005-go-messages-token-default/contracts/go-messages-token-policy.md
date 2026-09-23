# Contract: Go Messages Output-token Policy

For every direct request to the Go Messages endpoint, the JSON body contains:

```json
{"model": "<reviewed Go Messages model>", "messages": [], "max_tokens": 8192}
```

When an explicit validated `max_tokens` is supplied through the existing client
construction path, that final value replaces `8192`. This contract applies only
to the direct Go Messages adapter; it does not change endpoint selection,
authentication headers, session identity, tools, structured output, error
mapping, or any other provider.
