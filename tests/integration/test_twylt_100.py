"""Integration test for the published TWYLT 1.0.0 contract.

Runs against the installed PyPI dependency by default. TWYLT_REPO can point to
a GitHub checkout to verify the same public executable contract from source.
"""
import os
import sys
from pathlib import Path
import pytest
from toolpack_builder.probe import probe


def _example_path() -> Path:
    repo = os.getenv("TWYLT_REPO")
    if repo:
        path = Path(repo) / "examples/list_directory/run.py"
        if not path.is_file():
            pytest.fail(f"TWYLT_REPO has no examples/list_directory/run.py: {repo}")
        return path
    pytest.skip("set TWYLT_REPO to a TWYLT checkout for the upstream example integration test")


def test_twylt_100_list_directory_contract(monkeypatch):
    path = _example_path()
    repo = path.parents[2]
    old = os.environ.get("PYTHONPATH", "")
    monkeypatch.setenv("PYTHONPATH", str(repo / "src") + (os.pathsep + old if old else ""))
    spec = probe(path, install_missing=False)
    assert spec.declared_name == "list-directory"
    assert spec.version == "1.0.0"
    assert spec.description == "List entries in a directory."
    assert spec.input_schema["type"] == "object"
    assert "path" in spec.input_schema["properties"]
    assert spec.output_schema["type"] == "object"
    assert spec.few_shots
