# ADR 0003: Install missing probe dependencies in isolation

Status: accepted

## Decision

First request ToolSpec `json_spec`. If static introspection returns missing schemas and declares pip requirements, install them with pip into a temporary target and retry with that target prepended to `PYTHONPATH`.

Do not install discovered tool dependencies into Builder's environment as a side effect of scanning.
