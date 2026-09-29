# ADR 0010: Migrate the tool contract from ToolSpec to TWYLT

## Status
Accepted in 0.4.0.

## Context
ToolSpec was renamed to TWYLT. TWYLT 1.0.0 succeeds ToolSpec 1.6.2 and publishes protocol 1.8. The public discovery contract remains process-based through `INPUT_DESCRIBE=json_spec`, and the reference bootstrap is `twylt.bootstrap.run_tool_file`.

## Decision
ToolPack Builder 0.4.0 targets TWYLT >=1.0.0. Generated ToolHub tools depend on `twylt>=1.0.0` and use the TWYLT bootstrap. Current code and user-facing terminology use TWYLT. Historical ADRs and changelog entries keep the ToolSpec name because they describe releases that actually used it.

The builder continues to discover tools through the executable protocol rather than importing TWYLT implementation classes. This preserves the project boundary established by ADR 0001.

## Verification
The cumulative offline suite validates the process and ToolHub contracts. An upstream integration test can be enabled with `TWYLT_REPO` and runs against `examples/list_directory/run.py` from the TWYLT repository.
