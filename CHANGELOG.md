# Changelog

## 0.3.1

- Fixed GUI startup diagnostics: CustomTkinter and stdlib tkinter are diagnosed separately.
- Error now shows the exact Python interpreter and original import error.
- Fixed tkinter dialog/messagebox scope inside the GUI application.
- Added regression coverage for GUI import/bootstrap behavior.

## 0.3.0
- Added optional CustomTkinter GUI (`toolpack-builder-gui`).
- Added core progress events and build-from-scan API.
- Added configuration fingerprints to prevent stale GUI builds.
- Added persistent project/settings storage.
- Added single and directory-tree category strategies.
- Added report and raw ToolPack viewers.
- Kept GUI dependencies optional for headless CLI use.

## 0.2.0 - 2026-09-25

- Added a per-scan isolated dependency cache; identical pip requirement sets are installed once and reused across probes.
- Dependency targets are cleaned up at the end of each scan.
- Added ToolHub `TOOLHUB_PACK` v1 contract validation before writing artifacts.
- Added JSON round-trip regression coverage for generated ToolHub packs.
- Added an opt-in integration test against the published ToolSpec 1.6.1 `examples/list_directory/run.py`.
- Added ADRs for dependency caching and upstream contract testing.
- Preserved 0.1.1 ToolSpec-name and glob/hidden-path behavior.

## 0.1.1 - 2026-09-25

- ToolHub tool names now come from ToolSpec `name` instead of the source filename.
- Hidden files and files below hidden directories are always excluded, including `.venv` at any depth.
- Include and exclude patterns now share consistent path-glob semantics; `**` matches arbitrary nesting (including zero directories).
- Added regression tests for hidden paths, deep exclusions, root/deep `**` includes, and duplicate ToolSpec names.

## 0.1.0 - 2026-09-25

- Initial standalone CLI release.
- Recursive glob discovery and exclusions.
- ToolSpec `json_spec` probing with isolated pip dependency retry.
- ToolHub `TOOLHUB_PACK` v1 generation.
- Tool names derived from source filenames; duplicate detection.
- ToolSpec-style bootstrap using absolute discovered paths.
- Human/JSON diagnostics, debug mode and environment overrides.
- ADRs, cumulative regression tests, MIT license and release version verification.
