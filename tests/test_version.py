import re
from pathlib import Path
import toolpack_builder

def test_version_matches_pyproject():
    text = (Path(__file__).parents[1]/"pyproject.toml").read_text()
    version = re.search(r'^version = "([^"]+)"', text, re.M).group(1)
    assert toolpack_builder.__version__ == version
