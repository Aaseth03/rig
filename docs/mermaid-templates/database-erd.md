# Database ERD Template

An `erDiagram` for documenting relational schema: entities, attributes,
keys, and relationships.

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        uuid id PK
        string email UK
        string name
        timestamp created_at
    }

    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        uuid id PK
        uuid user_id FK
        string status
        numeric total
        timestamp created_at
    }

    ORDER_ITEM }o--|| PRODUCT : references
    ORDER_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        numeric unit_price
    }

    PRODUCT {
        uuid id PK
        string sku UK
        string name
        numeric price
    }

    USER ||--o| ADDRESS : "has default"
    ADDRESS {
        uuid id PK
        uuid user_id FK
        string line1
        string city
        string postal_code
    }
```

## Relationship cardinality cheat sheet

| Left | Right | Meaning |
|---|---|---|
| `\|o` | `o\|` | zero or one |
| `\|\|` | `\|\|` | exactly one |
| `}o` | `o{` | zero or more |
| `}\|` | `\|{` | one or more |

Combine as `LEFT_ENTITY <left><right>--<right><left> RIGHT_ENTITY : verb`,
e.g. `USER ||--o{ ORDER : places` reads "one user places zero or more
orders."

## Notes

- Mark keys with `PK` (primary), `FK` (foreign), `UK` (unique) after the
  type in each attribute row.
- Label the relationship verb from the perspective of the left entity
  (`places`, `contains`, `references`) — makes the diagram read like a
  sentence.
- Keep attribute lists to what matters for the relationship being
  documented; this isn't a full migration/schema dump.
