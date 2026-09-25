from pathlib import Path
from toolpack_builder.dependencies import DependencyCache
import toolpack_builder.dependencies as deps


def test_dependency_cache_installs_identical_requirements_once(monkeypatch):
    calls = []
    class P:
        returncode = 0; stderr = ""; stdout = ""
    def fake_run(cmd, **kwargs):
        calls.append(cmd); return P()
    monkeypatch.setattr(deps.subprocess, "run", fake_run)
    with DependencyCache(python="python-test") as cache:
        a = cache.install("pydantic>=2\n")
        b = cache.install("pydantic>=2   \n\n")
        assert a == b
        assert cache.entries == 1
    assert len(calls) == 1


def test_dependency_cache_separates_different_requirements(monkeypatch):
    calls = []
    class P:
        returncode = 0; stderr = ""; stdout = ""
    monkeypatch.setattr(deps.subprocess, "run", lambda cmd, **kwargs: calls.append(cmd) or P())
    with DependencyCache() as cache:
        assert cache.install("a==1") != cache.install("a==2")
    assert len(calls) == 2
