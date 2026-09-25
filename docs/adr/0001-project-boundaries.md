# ADR 0001: Keep Builder independent from ToolSpec and ToolHub

Status: accepted

## Decision

ToolPack Builder is a standalone Python project. It consumes ToolSpec through its public executable introspection protocol (`INPUT_DESCRIBE=json_spec`) and emits ToolHub's public `.toolpack` JSON format. It does not import ToolHub internals or ToolSpec implementation classes to discover tools.

The package depends on ToolSpec only so the reference bootstrap is available at probe/runtime; metadata flow remains process/protocol based.

## Consequences

ToolSpec, Builder, and ToolHub can evolve independently. Compatibility boundaries are explicit and testable.
