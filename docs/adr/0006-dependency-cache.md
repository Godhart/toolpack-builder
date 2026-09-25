# ADR 0006: Per-scan dependency cache

## Status
Accepted in 0.2.0.

## Decision
A scan owns one isolated dependency cache. Requirements with identical normalized content and Python executable share one `pip --target` installation. Targets live only for the scan and are removed afterwards.

## Rationale
Tool directories commonly contain many tools with the same dependencies. Installing the same set for every candidate is slow and produces unnecessary network/package-manager work. A per-scan cache preserves isolation from ToolHub and the user's interpreter while avoiding duplicate installs.
