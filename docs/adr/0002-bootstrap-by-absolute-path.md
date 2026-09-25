# ADR 0002: Bootstrap references discovered source by absolute path

Status: accepted for 0.1.x

## Context

ToolHub stores one code file plus one dependency manifest for a native tool. The requested design is to use the ToolSpec example bootstrap rather than copying business code into ToolHub.

## Decision

Generate the same `run_tool_file(Path(...))` bootstrap pattern as ToolSpec `examples/list_directory/run.py`, with an absolute path to the discovered file.

## Consequences

The source tree must exist at runtime on the ToolHub host. Packs are not yet self-contained. A future vendored-source mode may change this without changing discovery.
