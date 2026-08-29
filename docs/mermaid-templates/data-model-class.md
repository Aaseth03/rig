# Data Model / Class Diagram Template

A `classDiagram` for domain models, DTOs, and service interfaces —
useful for documenting an object model or a typed API contract.

```mermaid
classDiagram
    class User {
        +UUID id
        +String email
        +String name
        -String passwordHash
        +authenticate(password) bool
    }

    class Order {
        +UUID id
        +UUID userId
        +OrderStatus status
        +Decimal total
        +addItem(item) void
        +submit() void
    }

    class OrderItem {
        +UUID id
        +UUID productId
        +int quantity
        +Decimal unitPrice
    }

    class Product {
        +UUID id
        +String sku
        +String name
        +Decimal price
    }

    class OrderStatus {
        <<enumeration>>
        PENDING
        PAID
        SHIPPED
        CANCELLED
    }

    class OrderRepository {
        <<interface>>
        +findById(id) Order
        +save(order) void
    }

    User "1" --> "*" Order : places
    Order "1" *-- "many" OrderItem : contains
    OrderItem "many" --> "1" Product : references
    Order --> OrderStatus : has
    OrderRepository ..> Order : persists
```

## Relationship cheat sheet

| Syntax | Meaning |
|---|---|
| `A --> B` | association |
| `A --\|> B` | inheritance (A extends B) |
| `A ..\|> B` | realization (A implements interface B) |
| `A *-- B` | composition (B can't exist without A) |
| `A o-- B` | aggregation (B can exist without A) |
| `A ..> B` | dependency (A uses B) |

`+` public, `-` private, `#` protected, `~` package/internal.
`<<interface>>` / `<<enumeration>>` / `<<abstract>>` as stereotypes.

## Notes

- Good for capturing a domain model before writing types/interfaces, or
  for documenting an existing one during a review/handoff.
- Keep method signatures to the public contract — skip implementation
  details and private helpers that don't affect callers.
- For pure database schema (tables/FKs), prefer
  [database-erd.md](database-erd.md) instead — `classDiagram` is for
  behavior-bearing objects, not row storage.
