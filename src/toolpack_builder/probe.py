from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from .dependencies import DependencyCache, DependencyError
from .models import TwyltData

class ProbeError(RuntimeError):
    pass


def _run(path: Path, mode: str, python: str, timeout: float, extra_pythonpath: Path | None = None) -> Any:
    env = os.environ.copy()
    env["INPUT_DESCRIBE"] = mode
    if extra_pythonpath:
        old = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(extra_pythonpath) + (os.pathsep + old if old else "")
    proc = subprocess.run([python, str(path)], cwd=str(path.parent), env=env,
                          text=True, capture_output=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit status {proc.returncode}"
        raise ProbeError(detail)
    text = proc.stdout.strip()
    if not text:
        raise ProbeError(f"empty INPUT_DESCRIBE={mode} response")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProbeError(f"invalid JSON from INPUT_DESCRIBE={mode}: {exc}") from exc


def _to_spec(path: Path, data: dict[str, Any]) -> TwyltData:
    req = data.get("requirements") or {}
    if not isinstance(req, dict):
        raise ProbeError("json_spec.requirements must be an object")
    return TwyltData(path=path, description=str(data.get("description") or ""),
        requirements_tool=str(req.get("tool") or ""), requirements_format=str(req.get("format") or "requirements.txt"),
        requirements_content=str(req.get("content") or ""), input_schema=data.get("input_schema") or data.get("inputSchema") or {},
        output_schema=data.get("output_schema") or data.get("outputSchema") or {}, few_shots=data.get("few_shots") or [],
        declared_name=data.get("name"), version=data.get("version"))


def probe(path: Path, python: str = sys.executable, timeout: float = 10.0, install_missing: bool = True, dependency_cache: DependencyCache | None = None) -> TwyltData:
    data = _run(path, "json_spec", python, timeout)
    if not isinstance(data, dict):
        raise ProbeError("json_spec must be a JSON object")
    spec = _to_spec(path, data)
    # TWYLT deliberately returns static metadata + empty schemas when an import
    # is missing. Install declared pip deps in isolation, then retry introspection.
    if install_missing and spec.requirements_content.strip() and (not spec.input_schema or not spec.output_schema):
        if spec.requirements_tool and spec.requirements_tool != "pip":
            raise ProbeError(f"automatic dependency installation only supports pip, got {spec.requirements_tool!r}")
        try:
            if dependency_cache is None:
                dependency_cache = DependencyCache(python=python)
            target = dependency_cache.install(spec.requirements_content)
        except DependencyError as exc:
            raise ProbeError(f"dependency installation failed: {exc}") from exc
        data = _run(path, "json_spec", python, timeout, target)
        if not isinstance(data, dict):
            raise ProbeError("json_spec must be a JSON object after dependency installation")
        spec = _to_spec(path, data)
    if not spec.input_schema or not spec.output_schema:
        raise ProbeError("TWYLT schemas are unavailable after probing")
    return spec
