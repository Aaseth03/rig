# CI/CD Pipeline Template

A flowchart for documenting a build/test/deploy pipeline, including gates
and rollback paths.

```mermaid
flowchart TD
    Push[/Push to branch/] --> Lint{{Lint}}
    Lint -->|fail| Fail1[[Report failure]]
    Lint -->|pass| Test{{Unit + Integration Tests}}
    Test -->|fail| Fail1
    Test -->|pass| Build[Build artifact]
    Build --> Scan{{Security scan}}
    Scan -->|fail| Fail1
    Scan -->|pass| Gate{On main branch?}

    Gate -->|no| Preview[Deploy preview env]
    Preview --> End1((Done))

    Gate -->|yes| Approval{{Manual approval}}
    Approval -->|rejected| Fail1
    Approval -->|approved| Staging[Deploy to staging]
    Staging --> Smoke{{Smoke tests}}
    Smoke -->|fail| Rollback[Rollback staging]
    Smoke -->|pass| Prod[Deploy to production]
    Prod --> Monitor{{Monitor error rate}}
    Monitor -->|spike| RollbackProd[Rollback production]
    Monitor -->|healthy| End2((Done))

    Fail1 --> End3(((Stopped)))
    Rollback --> End3
    RollbackProd --> End3
```

## Notes

- Use `{{Text}}` (hexagon) for gates/checks — lint, tests, scans, manual
  approval — so they visually stand apart from `[Text]` action steps.
- Use `{Text}` (rhombus) sparingly, only for a true binary branch
  (`Gate`) — keep hexagons for pass/fail checks that also have a failure
  exit.
- Route every failure path to a single terminal node (`Fail1` /
  `End3`) rather than dead-ending arrows — makes rollback/failure
  handling easy to audit at a glance.
- `[/Text/]` (parallelogram) marks the external trigger (a push, a
  webhook, a cron) that kicks off the pipeline.
- Swap `flowchart TD` for `flowchart LR` if the pipeline has more stages
  than fit comfortably top-to-bottom in a doc.
