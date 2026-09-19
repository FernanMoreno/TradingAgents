# Data Model: Go Role Eligibility

## Go Model Capability

| Field | Meaning | Source |
|---|---|---|
| Model identifier | Strict reviewed OpenCode Go ID | Existing Go catalog |
| Protocol | Wire protocol required by that ID | Existing Go catalog |
| Ordinary tools | Whether the model can bind ordinary analyst tools | Existing reviewed metadata |

## Thinking Role Eligibility

| Role | Eligibility rule | Consequence when false |
|---|---|---|
| Quick | A Messages model must support ordinary tools; other existing protocol paths retain their current behavior. | Exclude from picker; reject known model before graph initialization. |
| Deep | Any reviewed Go ID. | Remains selectable. |

## Invariants

- The model identifier remains strict and is never sent using a guessed
  protocol.
- A capability check is pure: it does not read a credential, send a request,
  create a client, or change configuration.
- Only a known reviewed model can be rejected for role eligibility; unknown
  identifiers continue to the established strict factory validation.
- Deep availability is not inferred from Quick eligibility.
