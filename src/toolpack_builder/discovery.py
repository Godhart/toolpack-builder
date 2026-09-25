from __future__ import annotations
import re
from functools import lru_cache
from pathlib import Path, PurePosixPath


def _is_hidden(rel: PurePosixPath) -> bool:
    """Exclude a hidden file or anything below a hidden directory."""
    return any(part.startswith(".") for part in rel.parts)


@lru_cache(maxsize=256)
def _glob_regex(pattern: str) -> re.Pattern[str]:
    """Compile a path glob where *, ?, [] stay within a segment and ** crosses '/'."""
    pattern = pattern.replace("\\", "/").lstrip("./")
    out: list[str] = ["^"]
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                i += 2
                # **/ means zero or more complete path segments.
                if i < len(pattern) and pattern[i] == "/":
                    out.append("(?:.*/)?")
                    i += 1
                else:
                    out.append(".*")
                continue
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "[":
            j = i + 1
            if j < len(pattern) and pattern[j] in "!^":
                j += 1
            if j < len(pattern) and pattern[j] == "]":
                j += 1
            while j < len(pattern) and pattern[j] != "]":
                j += 1
            if j >= len(pattern):
                out.append(r"\[")
            else:
                stuff = pattern[i + 1:j]
                if stuff.startswith("!"):
                    stuff = "^" + stuff[1:]
                elif stuff.startswith("^"):
                    stuff = "\\" + stuff
                out.append("[" + stuff + "]")
                i = j
        else:
            out.append(re.escape(c))
        i += 1
    out.append("$")
    return re.compile("".join(out))


def path_glob_match(path: PurePosixPath | str, pattern: str) -> bool:
    value = path.as_posix() if isinstance(path, PurePosixPath) else str(path).replace("\\", "/")
    return bool(_glob_regex(pattern).match(value))


def discover(root: Path, pattern: str, excludes: tuple[str, ...] = ()) -> list[Path]:
    root = root.resolve()
    result: list[Path] = []
    # Use the same matcher for include and exclude patterns. rglob('*') also lets
    # us apply the explicit hidden-path rule consistently at every depth.
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = PurePosixPath(path.relative_to(root).as_posix())
        if _is_hidden(rel):
            continue
        if not path_glob_match(rel, pattern):
            continue
        if any(path_glob_match(rel, p) for p in excludes):
            continue
        result.append(path.resolve())
    return sorted(set(result), key=lambda p: p.as_posix())
