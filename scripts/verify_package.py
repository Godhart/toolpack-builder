from pathlib import Path
import re
import sys
root = Path(__file__).parents[1]
pyproject = (root/'pyproject.toml').read_text(encoding='utf-8')
version = re.search(r'^version = "([^"]+)"', pyproject, re.M).group(1)
init = (root/'src/toolpack_builder/__init__.py').read_text(encoding='utf-8')
if f'__version__ = "{version}"' not in init:
    raise SystemExit('version mismatch: pyproject.toml vs __init__.py')
readme = (root/'README.md').read_text(encoding='utf-8')
if version not in readme:
    raise SystemExit('README does not mention current version')
if not (root/'LICENSE').exists():
    raise SystemExit('LICENSE missing')
print(f'package verification OK: {version}')
