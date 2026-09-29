from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass(slots=True)
class TwyltData:
    path: Path
    description: str
    requirements_tool: str
    requirements_format: str
    requirements_content: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    few_shots: list[Any]
    declared_name: str | None = None
    version: str | None = None

@dataclass(slots=True)
class ScanItem:
    path: Path
    status: str
    message: str = ""
    spec: TwyltData | None = None

@dataclass(slots=True)
class ScanReport:
    root: Path
    items: list[ScanItem] = field(default_factory=list)

    @property
    def valid(self) -> list[ScanItem]:
        return [x for x in self.items if x.status == "valid"]

    @property
    def failed(self) -> list[ScanItem]:
        return [x for x in self.items if x.status == "failed"]
