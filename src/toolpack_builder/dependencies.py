from __future__ import annotations
import hashlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

class DependencyError(RuntimeError):
    pass


def _normalize_requirements(content: str) -> str:
    # Preserve requirement semantics/order while making inconsequential trailing
    # whitespace and blank lines share one cache entry.
    return "\n".join(line.rstrip() for line in content.strip().splitlines()) + "\n"


@dataclass
class DependencyCache:
    """Per-scan cache of isolated pip targets, keyed by requirement content."""
    python: str = sys.executable
    install_timeout: float = 180.0
    _targets: dict[str, Path] = field(default_factory=dict)
    _temps: list[tempfile.TemporaryDirectory] = field(default_factory=list)

    def install(self, requirements: str) -> Path:
        normalized = _normalize_requirements(requirements)
        key = hashlib.sha256((self.python + "\0" + normalized).encode()).hexdigest()
        if key in self._targets:
            return self._targets[key]
        tmp = tempfile.TemporaryDirectory(prefix="toolpack_builder_deps_")
        self._temps.append(tmp)
        target = Path(tmp.name)
        req = target / "_requirements.txt"
        req.write_text(normalized, encoding="utf-8")
        p = subprocess.run(
            [self.python, "-m", "pip", "install", "--disable-pip-version-check", "--target", str(target), "-r", str(req)],
            text=True, capture_output=True, timeout=self.install_timeout, check=False,
        )
        if p.returncode:
            raise DependencyError(p.stderr.strip() or p.stdout.strip() or f"pip exit status {p.returncode}")
        self._targets[key] = target
        return target

    @property
    def entries(self) -> int:
        return len(self._targets)

    def close(self) -> None:
        while self._temps:
            self._temps.pop().cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
