from __future__ import annotations
import json, os
from dataclasses import asdict, dataclass, field
from pathlib import Path

@dataclass(slots=True)
class ProjectConfig:
    source: str = ""
    include: str = "**/*.py"
    excludes: list[str] = field(default_factory=lambda: ["**/__pycache__/**", "**/test_*.py", "**/tests/**", "**/run.py"])
    output: str = ""
    category_mode: str = "single"
    category_name: str = "Tools"

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ProjectConfig":
        return cls(**json.loads(path.read_text(encoding="utf-8")))

def config_dir() -> Path:
    if os.name == "nt":
        return Path(os.getenv("APPDATA", Path.home()/"AppData/Roaming"))/"toolpack-builder"
    return Path(os.getenv("XDG_CONFIG_HOME", Path.home()/".config"))/"toolpack-builder"

def settings_path() -> Path: return config_dir()/"settings.json"
def default_project_path() -> Path: return config_dir()/"projects"/"default.json"
