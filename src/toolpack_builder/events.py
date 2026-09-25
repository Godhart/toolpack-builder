from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

@dataclass(frozen=True, slots=True)
class BuildEvent:
    kind: str
    current: int = 0
    total: int = 0
    path: Path | None = None
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

EventHandler = Callable[[BuildEvent], None]

def emit(handler: EventHandler | None, kind: str, **kwargs: Any) -> None:
    if handler is not None:
        handler(BuildEvent(kind=kind, **kwargs))
