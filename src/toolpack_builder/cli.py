from __future__ import annotations
import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from . import __version__
from .builder import BuildConfig, build, scan


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="toolpack-builder", description="Build ToolHub .toolpack files from TWYLT tools")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--debug", action="store_true", default=os.getenv("TOOLPACK_BUILDER_DEBUG", "").lower() in {"1","true","yes","on"})
    p.add_argument("--error-format", choices=("human", "json"), default=os.getenv("TOOLPACK_BUILDER_ERROR_FORMAT", "human"))
    sub = p.add_subparsers(dest="command", required=True)
    for command in ("scan", "build"):
        q = sub.add_parser(command)
        q.add_argument("root", type=Path)
        q.add_argument("--glob", default="**/*.py")
        q.add_argument("--exclude", action="append", default=[])
        q.add_argument("--python", default=sys.executable)
        q.add_argument("--probe-timeout", type=float, default=10.0)
        q.add_argument("--json", action="store_true", help="machine-readable command output")
        q.add_argument("--runner-type", default="python_local")
        q.add_argument("--runner-name", default="Python")
    b = sub.choices["build"]
    b.add_argument("--output", "-o", type=Path, required=True)
    b.add_argument("--category-name")
    b.add_argument("--timeout-ms", type=int, default=30000)
    return p


def _config(a) -> BuildConfig:
    defaults = ("**/__pycache__/**", "**/test_*.py", "**/tests/**", "**/run.py")
    return BuildConfig(root=a.root, glob=a.glob, excludes=defaults + tuple(a.exclude), python=a.python,
                       probe_timeout=a.probe_timeout, category_name=getattr(a,"category_name",None),
                       runner_type=a.runner_type, runner_name=a.runner_name, timeout_ms=getattr(a,"timeout_ms",30000))


def _report_dict(r):
    return {"root": str(r.root), "found": len(r.items), "valid": len(r.valid), "failed": len(r.failed),
            "items": [{"path": str(x.path), "status": x.status, "message": x.message} for x in r.items]}


def main(argv=None) -> int:
    a = _parser().parse_args(argv)
    try:
        cfg = _config(a)
        if a.command == "scan":
            r = scan(cfg)
            if a.json:
                print(json.dumps(_report_dict(r), ensure_ascii=False, indent=2))
            else:
                for x in r.items:
                    mark = "✓" if x.status == "valid" else "✗"
                    rel = x.path.relative_to(r.root)
                    suffix = f" — {x.message}" if x.message else ""
                    print(f"{mark} {rel} [{x.status}]{suffix}")
                print(f"Found {len(r.items)}; valid {len(r.valid)}; failed {len(r.failed)}")
            return 0 if not r.failed else 1
        result = build(cfg, a.output)
        if a.json:
            print(json.dumps({**_report_dict(result.report), "output": str(a.output)}, ensure_ascii=False, indent=2))
        else:
            print(f"Built {a.output}: {len(result.report.valid)} tool(s), {len(result.report.failed)} failed candidate(s)")
            print(f"Runner required in ToolHub: {cfg.runner_name} ({cfg.runner_type})")
        return 0 if not result.report.failed else 1
    except Exception as exc:
        if a.error_format == "json":
            error = {"error": {"type": type(exc).__name__, "message": str(exc), "source": "toolpack-builder"}}
            if a.debug: error["error"]["traceback"] = traceback.format_exc()
            print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        else:
            print(f"toolpack-builder: {type(exc).__name__}: {exc}", file=sys.stderr)
            if a.debug: traceback.print_exc()
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
