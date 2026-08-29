# Request Sequence Template

A `sequenceDiagram` for documenting an API request/response flow —
authentication, error paths, and async work included.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant FE as Frontend
    participant API as API Gateway
    participant Auth as Auth Service
    participant Svc as Orders Service
    participant DB as Database
    participant Q as Queue

    User->>FE: Click "Place order"
    FE->>API: POST /orders (Bearer token)
    API->>Auth: Validate token
    alt token invalid
        Auth-->>API: 401 Unauthorized
        API-->>FE: 401 Unauthorized
        FE-->>User: Show "please log in"
    else token valid
        Auth-->>API: OK (user id)
        API->>Svc: Create order
        Svc->>DB: INSERT order
        DB-->>Svc: order id
        Svc-)Q: publish OrderCreated
        Svc-->>API: 201 Created
        API-->>FE: 201 Created
        FE-->>User: Show confirmation
        Q--)Svc: (async) OrderCreated consumed
        Svc->>DB: UPDATE order status
    end
```

## Notes

- `->>` = request (solid, filled arrow), `-->>` = response (dashed).
- `-)` / `--)` = async/fire-and-forget messages (open arrowhead) — use for
  queue publishes and event consumption.
- `alt / else / end` for branching paths (success vs error); use `opt` for
  a single optional branch and `par / and / end` for parallel calls.
- `actor` renders a stick figure for humans; `participant` renders a box —
  reserve `actor` for the end user.
- `autonumber` is worth keeping on for anything you'll reference in code
  review comments ("see step 4").
