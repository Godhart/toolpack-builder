"""Integration test for the published ToolSpec 1.6.1 contract.

Runs only when TOOLSPEC_REPO points to a ToolSpec 1.6.1 checkout. This keeps the
normal test suite offline/reproducible while CI can exercise the real upstream.
"""
import os
from pathlib import Path
import pytest
from toolpack_builder.probe import probe


def test_published_toolspec_161_list_directory(monkeypatch):
    root = os.getenv("TOOLSPEC_REPO")
    if not root:
        pytest.skip("set TOOLSPEC_REPO to a ToolSpec 1.6.1 checkout")
    repo = Path(root)
    pyproject = (repo / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.6.1"' in pyproject
    old = os.environ.get("PYTHONPATH", "")
    monkeypatch.setenv("PYTHONPATH", str(repo / "src") + (os.pathsep + old if old else ""))
    spec = probe(repo / "examples/list_directory/run.py", install_missing=False)
    assert spec.declared_name == "list-directory"
    assert spec.version == "1.0.0"
    assert spec.description == "List entries in a directory."
    assert spec.input_schema["type"] == "object"
    assert "path" in spec.input_schema["properties"]
    assert spec.output_schema["type"] == "object"
    assert spec.few_shots
