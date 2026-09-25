import json
from pathlib import Path
from toolpack_builder.builder import BuildConfig, build

TOOL = r'''import json, os
if os.getenv("INPUT_DESCRIBE") == "json_spec":
    print(json.dumps({
      "format_version":"1.0", "name":"declared-name", "version":"1.2.3",
      "description":"Demo tool", "requirements":{"tool":"pip","format":"requirements.txt","content":""},
      "input_schema":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]},
      "output_schema":{"type":"object","properties":{"ok":{"type":"boolean"}},"required":["ok"]},
      "few_shots":[{"input":{"path":"."},"output":{"ok":True}}]
    }))
else:
    raise SystemExit(3)
'''

def test_build_uses_toolspec_name_and_toolhub_v1_format(tmp_path: Path):
    root = tmp_path / "my_tools"; root.mkdir()
    tool = root / "hello.py"; tool.write_text(TOOL)
    out = tmp_path / "x.toolpack"
    result = build(BuildConfig(root=root), out)
    p = json.loads(out.read_text())
    assert p["kind"] == "TOOLHUB_PACK" and p["version"] == 1
    t = p["category"]["tools"][0]
    assert t["name"] == "declared-name"
    assert t["runnerType"] == "python_local"
    assert "run_tool_file" in t["code"]
    assert str(tool.resolve()) in t["code"]
    assert t["packageJson"].startswith("toolspec>=1.6.1\n")
    assert len(result.report.valid) == 1

def test_nested_glob_and_default_excludes(tmp_path: Path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "a.py").write_text(TOOL)
    (tmp_path / "nested" / "run.py").write_text(TOOL)
    r = build(BuildConfig(root=tmp_path))
    assert [x.path.name for x in r.report.valid] == ["a.py"]

def test_duplicate_toolspec_name_is_error(tmp_path: Path):
    for d, filename in (("a", "one.py"), ("b", "two.py")):
        (tmp_path/d).mkdir(); (tmp_path/d/filename).write_text(TOOL)
    try:
        build(BuildConfig(root=tmp_path))
    except ValueError as e:
        assert "duplicate tool name" in str(e)
    else:
        raise AssertionError("expected duplicate error")

def test_hidden_files_and_hidden_parent_directories_are_always_excluded(tmp_path: Path):
    (tmp_path / ".hidden.py").write_text(TOOL)
    (tmp_path / ".venv" / "lib" / "python" / "site-packages").mkdir(parents=True)
    (tmp_path / ".venv" / "lib" / "python" / "site-packages" / "tool.py").write_text(TOOL)
    (tmp_path / "deep" / ".cache" / "more").mkdir(parents=True)
    (tmp_path / "deep" / ".cache" / "more" / "cached.py").write_text(TOOL)
    (tmp_path / "visible").mkdir()
    (tmp_path / "visible" / "ok.py").write_text(TOOL.replace('"declared-name"', '"visible-tool"'))
    r = build(BuildConfig(root=tmp_path))
    assert [x.path.relative_to(tmp_path).as_posix() for x in r.report.valid] == ["visible/ok.py"]


def test_exclude_double_star_matches_arbitrary_nesting(tmp_path: Path):
    (tmp_path / "a" / "b" / "generated" / "c").mkdir(parents=True)
    (tmp_path / "a" / "b" / "generated" / "c" / "skip.py").write_text(TOOL)
    (tmp_path / "a" / "b" / "keep").mkdir(parents=True)
    (tmp_path / "a" / "b" / "keep" / "yes.py").write_text(TOOL.replace('"declared-name"', '"keep-tool"'))
    cfg = BuildConfig(root=tmp_path, excludes=("**/generated/**",))
    r = build(cfg)
    assert [x.path.name for x in r.report.valid] == ["yes.py"]


def test_include_double_star_matches_root_and_deep_files(tmp_path: Path):
    (tmp_path / "root_tool.py").write_text(TOOL.replace('"declared-name"', '"root-tool"'))
    (tmp_path / "a" / "b").mkdir(parents=True)
    (tmp_path / "a" / "b" / "deep_tool.py").write_text(TOOL.replace('"declared-name"', '"deep-tool"'))
    r = build(BuildConfig(root=tmp_path, glob="**/*_tool.py"))
    assert {x.spec.declared_name for x in r.report.valid if x.spec} == {"root-tool", "deep-tool"}
