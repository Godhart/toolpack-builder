from __future__ import annotations
import hashlib, json, sys
from dataclasses import asdict, dataclass
from pathlib import Path
from .discovery import discover
from .dependencies import DependencyCache
from .events import EventHandler, emit
from .models import ScanItem, ScanReport
from .probe import ProbeError, probe
from .toolhub import pack, pack_from_paths, tool_entry, validate_pack_v1

@dataclass(slots=True)
class BuildConfig:
    root: Path
    glob: str = "**/*.py"
    excludes: tuple[str, ...] = ("**/__pycache__/**", "**/test_*.py", "**/tests/**", "**/run.py")
    python: str = sys.executable
    probe_timeout: float = 10.0
    category_name: str | None = None
    category_mode: str = "single"  # single | directories
    runner_type: str = "python_local"
    runner_name: str = "Python"
    timeout_ms: int = 30000

    def fingerprint(self) -> str:
        raw=json.dumps({k:(str(v) if isinstance(v,Path) else v) for k,v in asdict(self).items()}, sort_keys=True, default=list)
        return hashlib.sha256(raw.encode()).hexdigest()

@dataclass(slots=True)
class BuildResult:
    report: ScanReport
    payload: dict | None = None

def scan(config: BuildConfig, on_event: EventHandler | None = None) -> ScanReport:
    root=config.root.resolve(); report=ScanReport(root=root)
    emit(on_event,"discovery_started",message=str(root))
    paths=discover(root,config.glob,config.excludes)
    emit(on_event,"discovery_finished",total=len(paths),message=f"{len(paths)} candidate(s)")
    cache=DependencyCache(python=config.python)
    try:
        for i,path in enumerate(paths,1):
            emit(on_event,"probe_started",current=i,total=len(paths),path=path)
            try:
                spec=probe(path,config.python,config.probe_timeout,dependency_cache=cache)
                report.items.append(ScanItem(path,"valid",spec=spec)); emit(on_event,"probe_finished",current=i,total=len(paths),path=path,message="valid")
            except (ProbeError,OSError,TimeoutError) as exc:
                report.items.append(ScanItem(path,"failed",str(exc))); emit(on_event,"probe_finished",current=i,total=len(paths),path=path,message=str(exc))
            except Exception as exc:
                msg=f"{type(exc).__name__}: {exc}"; report.items.append(ScanItem(path,"failed",msg)); emit(on_event,"probe_finished",current=i,total=len(paths),path=path,message=msg)
    finally: cache.close()
    emit(on_event,"scan_finished",current=len(paths),total=len(paths),message=f"{len(report.valid)} ready, {len(report.failed)} failed")
    return report

def build_from_report(config: BuildConfig, report: ScanReport, output: Path|None=None, on_event: EventHandler|None=None) -> BuildResult:
    emit(on_event,"build_started",total=len(report.valid))
    names={}; entries=[]
    for i,item in enumerate(report.valid,1):
        assert item.spec
        name=(item.spec.declared_name or "").strip()
        if not name: raise ValueError(f"ToolSpec name is empty for {item.path}")
        if name in names: raise ValueError(f"duplicate tool name {name!r}: {names[name]} and {item.path}")
        names[name]=item.path; entries.append((item.path,tool_entry(item.spec,name,config.runner_type,config.runner_name,config.timeout_ms)))
        emit(on_event,"build_tool",current=i,total=len(report.valid),path=item.path,message=name)
    category=config.category_name or config.root.resolve().name
    payload=pack_from_paths(category,entries,report.root) if config.category_mode=="directories" else pack(category,[e for _,e in entries])
    validate_pack_v1(payload)
    if output:
        output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    emit(on_event,"build_finished",current=len(entries),total=len(entries),message=str(output or ""))
    return BuildResult(report,payload)

def build(config: BuildConfig, output: Path|None=None, on_event: EventHandler|None=None) -> BuildResult:
    return build_from_report(config,scan(config,on_event),output,on_event)
