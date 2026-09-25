import json
from pathlib import Path
from toolpack_builder.cli import main

BAD = 'print("not json")\n'

def test_scan_json_failure(tmp_path: Path, capsys):
    (tmp_path/"bad.py").write_text(BAD)
    rc = main(["scan", str(tmp_path), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert rc == 1 and data["failed"] == 1

def test_json_error_format(tmp_path: Path, capsys):
    rc = main(["--error-format","json","build",str(tmp_path),"-o",str(tmp_path/"x.toolpack")])
    # Empty packs are allowed in 0.1.0, so no framework error.
    assert rc == 0
