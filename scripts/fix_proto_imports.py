#!/usr/bin/env python3
"""Fix import paths in generated proto files."""

import re
from pathlib import Path


def fix_imports(file_path: Path) -> bool:
    """Fix import paths from 'protos.' to 'mysingle.protos.'"""
    content = file_path.read_text()
    original = content

    # Replace imports
    patterns = [
        (r"from protos\.", "from mysingle.protos."),
        (r"import protos\.", "import mysingle.protos."),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original:
        file_path.write_text(content)
        return True
    return False


def main():
    """Process all generated proto files."""
    proto_dir = Path(__file__).parent.parent / "src" / "mysingle" / "protos"

    if not proto_dir.exists():
        print(f"❌ Proto directory not found: {proto_dir}")
        return 1

    fixed_count = 0
    for py_file in proto_dir.rglob("*_pb2*.py"):
        if fix_imports(py_file):
            fixed_count += 1
            print(f"✅ Fixed: {py_file.relative_to(proto_dir)}")

    print(f"\n✅ Fixed {fixed_count} files")
    return 0


if __name__ == "__main__":
    exit(main())
