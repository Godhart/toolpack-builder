# ADR 0007: Upstream contract integration tests

## Status
Accepted in 0.2.0.

## Decision
Keep fast offline tests for the ToolHub v1 pack contract and an opt-in integration test against an actual ToolSpec 1.6.1 checkout (`TOOLSPEC_REPO`). Release verification runs the offline suite; CI/release candidates should additionally run the upstream integration test when the checkout is available.

## Rationale
The builder is intentionally independent of ToolSpec and ToolHub internals. Contract tests detect drift at those process/file boundaries without turning either project into a source dependency.
