from __future__ import annotations
import re
from pathlib import Path
from typing import Any
from .models import TwyltData


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "tool"


def bootstrap_code(tool_path: Path) -> str:
    # Same bootstrap pattern as TWYLT examples/list_directory/run.py.
    literal = repr(str(tool_path.resolve()))
    return (
        "from pathlib import Path\n"
        "from twylt.bootstrap import run_tool_file\n\n"
        f"run_tool_file(Path({literal}))\n"
    )


def runtime_requirements(spec: TwyltData) -> str:
    lines = ["twylt>=1.0.0"]
    content = spec.requirements_content.strip()
    if content:
        lines.append(content)
    return "\n".join(lines).rstrip() + "\n"


def tool_entry(spec: TwyltData, name: str, runner_type: str, runner_name: str, timeout_ms: int) -> dict[str, Any]:
    return {
        "name": name,
        "slug": slugify(name),
        "agentDescription": spec.description,
        "code": bootstrap_code(spec.path),
        "packageJson": runtime_requirements(spec),
        "inputSchema": spec.input_schema,
        "outputSchema": spec.output_schema,
        "examples": spec.few_shots,
        "timeoutMs": timeout_ms,
        "isMcpProxy": False,
        "mcpMethodName": None,
        "runnerType": runner_type,
        "runnerName": runner_name,
    }


def pack(category_name: str, tools: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": "TOOLHUB_PACK",
        "version": 1,
        "category": {
            "name": category_name,
            "slug": slugify(category_name),
            "appendPrompt": None,
            "type": "LOCAL",
            "remoteUrl": None,
            "remoteToken": None,
            "mcpCommand": None,
            "mcpArgs": None,
            "mcpEnv": {},
            "mcpIsStateful": False,
            "tools": tools,
            "children": [],
        },
    }

class ToolHubPackError(ValueError):
    pass


def validate_pack_v1(payload: dict[str, Any]) -> None:
    """Validate the ToolHub v1 import contract fields emitted by this builder."""
    if payload.get("kind") != "TOOLHUB_PACK" or payload.get("version") != 1:
        raise ToolHubPackError("expected TOOLHUB_PACK version 1")
    category = payload.get("category")
    if not isinstance(category, dict) or category.get("type") != "LOCAL":
        raise ToolHubPackError("pack.category must be a LOCAL category")
    if not isinstance(category.get("tools"), list) or not isinstance(category.get("children"), list):
        raise ToolHubPackError("category tools/children must be arrays")
    required = {"name", "slug", "agentDescription", "code", "packageJson", "inputSchema", "outputSchema", "examples", "timeoutMs", "isMcpProxy", "mcpMethodName", "runnerType", "runnerName"}
    def check(cat, where="category"):
        if not isinstance(cat.get("tools"), list) or not isinstance(cat.get("children"), list):
            raise ToolHubPackError(f"{where} tools/children must be arrays")
        for index, tool in enumerate(cat["tools"]):
            if not isinstance(tool, dict): raise ToolHubPackError(f"{where} tool {index} must be an object")
            missing = required - tool.keys()
            if missing: raise ToolHubPackError(f"{where} tool {index} missing fields: {', '.join(sorted(missing))}")
            if not isinstance(tool["inputSchema"], dict) or not isinstance(tool["outputSchema"], dict): raise ToolHubPackError(f"{where} tool {index} schemas must be objects")
        for i, child in enumerate(cat["children"]): check(child, f"{where}.children[{i}]")
    check(category)

def _category(name: str) -> dict[str, Any]:
    return {"name":name,"slug":slugify(name),"appendPrompt":None,"type":"LOCAL","remoteUrl":None,"remoteToken":None,"mcpCommand":None,"mcpArgs":None,"mcpEnv":{},"mcpIsStateful":False,"tools":[],"children":[]}

def pack_from_paths(category_name: str, entries: list[tuple[Path,dict[str,Any]]], root: Path) -> dict[str,Any]:
    top=_category(category_name)
    for path,tool in entries:
        node=top
        for part in path.relative_to(root).parent.parts:
            child=next((c for c in node["children"] if c["name"]==part),None)
            if child is None:
                child=_category(part); node["children"].append(child)
            node=child
        node["tools"].append(tool)
    return {"kind":"TOOLHUB_PACK","version":1,"category":top}
