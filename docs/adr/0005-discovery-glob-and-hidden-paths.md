# ADR 0005: Discovery glob semantics and hidden paths

## Status
Accepted.

## Context
The original implementation used `Path.glob()` for inclusion and `PurePath.match()` for exclusion. Those mechanisms do not provide identical path matching semantics, and exclusion patterns containing `**` could fail at some nesting depths. Virtual environments such as `.venv` also contain large Python trees that should never be treated as source tool candidates by default.

## Decision
ToolPack Builder uses one path-glob matcher for both include and exclude patterns. `*`, `?`, and character classes match within one path segment; `**` may span any number of path segments, including zero.

Independently of user patterns, a candidate is excluded when its own filename begins with `.` or any parent component relative to the scan root begins with `.`. Thus `.venv`, `.git`, `.cache`, and similar trees are ignored automatically at every depth.

Tool identity is not a discovery concern: after successful ToolSpec introspection, the ToolHub name is the ToolSpec-declared `name`.

## Consequences
- Include and exclude filters are predictable and symmetric.
- `.venv` and other hidden trees require no explicit exclusion.
- Duplicate detection operates on the actual ToolSpec names rather than filenames.
