# ADR 0008: Core events and CustomTkinter GUI

Status: accepted

## Decision
Long-running core operations expose typed `BuildEvent` callbacks. The GUI is an optional CustomTkinter frontend and never parses CLI output. It runs scan/build in worker threads and marshals events/results through a queue to the Tk main thread. GUI dependencies are optional (`[gui]`) so headless CLI installations remain lightweight.

A scan is bound to a deterministic configuration fingerprint. Build-from-report is enabled only while that fingerprint matches the current configuration.
