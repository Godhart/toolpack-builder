# ToolPack Builder 0.3.1

Standalone CLI builder that discovers **ToolSpec** Python tools and creates a ToolHub-compatible `.toolpack` (`TOOLHUB_PACK`, version 1).

It is intentionally a separate project. ToolSpec is the executable/introspection contract; ToolHub is the consumer of the generated artifact.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
pytest
python scripts/verify_package.py
```

## Scan

```bash
toolpack-builder scan ./tools --glob '**/*.py'
toolpack-builder scan ./tools --glob '**/*_tool.py' --json
```

Hidden paths are always excluded: any file whose name starts with `.` and any file below a directory whose name starts with `.` (for example `.venv/`, `.git/`, `.cache/`). Defaults also exclude `run.py`, `test_*.py`, `tests/`, and `__pycache__/`. Include and repeatable `--exclude` patterns use the same path-glob semantics: `*` stays within one path segment and `**` spans any number of directories, including zero.

Each candidate is executed with `INPUT_DESCRIBE=json_spec`. ToolSpec can return static metadata even when an import is missing. If schemas are unavailable and pip requirements are declared, Builder installs those requirements into an isolated temporary `--target` directory and retries introspection.

Since 0.2.0, identical requirement sets share one isolated installation for the duration of a scan. The cache is keyed by the Python executable and normalized requirements content, and is deleted after the scan. It never installs dependencies into ToolHub or the active environment.

## Build

```bash
toolpack-builder build ./tools \
  --glob '**/*.py' \
  --category-name my-tools \
  --output dist/my-tools.toolpack
```

The ToolHub tool name is taken from the ToolSpec `name` returned by `INPUT_DESCRIBE=json_spec`. Duplicate ToolSpec names are a build error; an empty ToolSpec name is also a build error.

Each generated ToolHub tool contains a minimal bootstrap equivalent to ToolSpec's `examples/list_directory/run.py`:

```python
from pathlib import Path
from toolspec.bootstrap import run_tool_file

run_tool_file(Path('/absolute/path/to/the/discovered/tool.py'))
```

The runtime requirements stored in ToolHub contain `toolspec>=1.6.1` plus the ToolSpec tool's declared requirements.

### Important: source path and ToolHub host

ToolHub executes the bootstrap in a temporary workspace, but the bootstrap points at the discovered tool by **absolute path**. Therefore the source tree must remain accessible at that same path on the machine running ToolHub. This is deliberate for 0.1.x and mirrors the requested design; vendoring source files into a pack is a possible later mode.

### Python runner

Current upstream ToolHub seeds Bun and Bash runners, not Python. Generated entries request:

- `runnerType = python_local`
- `runnerName = Python`

Create a matching ToolHub runner, for example with configuration conceptually equivalent to:

```json
{
  "codeFileName": "run.py",
  "depFileName": "requirements.txt",
  "installCmd": "python -m pip install -r requirements.txt",
  "runCmd": "python run.py"
}
```

You can override the identity with `--runner-type` and `--runner-name` to match an existing ToolHub installation.

## Diagnostics

Human output is the default. Machine-readable command output uses `--json`. Framework errors support:

```bash
toolpack-builder --error-format json build ...
toolpack-builder --debug ...
TOOLPACK_BUILDER_DEBUG=1 toolpack-builder ...
TOOLPACK_BUILDER_ERROR_FORMAT=json toolpack-builder ...
```

## Exit status

- `0`: command completed with no failed candidates
- `1`: scan/build completed but at least one candidate failed
- `2`: builder/configuration failure

A `.toolpack` is still written when some candidates fail; successful ToolSpec tools are retained. This makes directory scans useful while preserving a non-zero CI signal.

## Compatibility verification

The generated payload is validated against the ToolHub v1 fields before it is written, and the test suite verifies a JSON serialize/deserialize round trip. The contract mirrors current ToolHub export/import (`TOOLHUB_PACK`, version 1).

An opt-in integration test exercises the real published ToolSpec 1.6.1 example rather than a mock. With a ToolSpec 1.6.1 checkout:

```bash
TOOLSPEC_REPO=/path/to/toolspec pytest -q tests/integration/test_toolspec_161.py
```

The normal suite remains offline and reproducible; CI/release candidates should run both suites when the upstream checkout is available.

## Design records

See `docs/adr/`. Regression tests are cumulative: fixes should add tests rather than replacing old coverage.

## GUI (0.3.1)

Install the optional GUI dependency and start it:

```bash
pip install -e '.[gui]'
toolpack-builder-gui
```

The CustomTkinter GUI provides source/include/exclude configuration, output selection, single or directory-derived categories, separate Scan and Build actions, progress, report and raw ToolPack viewers, and persistent project parameters. Hidden paths remain automatically excluded by the core discovery layer.

GUI project state is stored under the platform config directory (`$XDG_CONFIG_HOME/toolpack-builder` or `~/.config/toolpack-builder` on Linux; `%APPDATA%\\toolpack-builder` on Windows). Scan results themselves are deliberately not persisted.


## GUI troubleshooting

If `toolpack-builder-gui` cannot start, it now distinguishes between a missing `customtkinter` pip package and a missing stdlib `tkinter` OS component. The diagnostic includes the exact Python interpreter used by the launcher. On Debian/Ubuntu, install the latter with `sudo apt install python3-tk`.
