#!/usr/bin/env python3
"""Fix import paths in CLI files after migration."""

import re
from pathlib import Path


def fix_imports(file_path: Path) -> bool:
    """Fix import paths from 'mysingle_protos' to 'mysingle'"""
    content = file_path.read_text()
    original = content

    # Replace imports
    patterns = [
        (r"from mysingle_protos\.cli\.", "from mysingle.cli.protos."),
        (r"import mysingle_protos\.cli\.", "import mysingle.cli.protos."),
        # For __version__ in __init__.py
        (r'__version__ = "2\.0\.4"', '__version__ = "1.0.0"'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original:
        file_path.write_text(content)
        return True
    return False


def main():
    """Process all CLI files."""
    cli_dir = Path(__file__).parent.parent / "src" / "mysingle" / "cli" / "protos"

    if not cli_dir.exists():
        print(f"❌ CLI directory not found: {cli_dir}")
        return 1

    fixed_count = 0
    for py_file in cli_dir.rglob("*.py"):
        if fix_imports(py_file):
            fixed_count += 1
            print(f"✅ Fixed: {py_file.relative_to(cli_dir.parent)}")

    print(f"\n✅ Fixed {fixed_count} files")
    return 0


if __name__ == "__main__":
    exit(main())
