#!/usr/bin/env python3
"""
Import 경로 자동 수정 스크립트
mysingle.base → mysingle.core.base
mysingle.logging → mysingle.core.logging
등으로 일괄 변경
"""

import re
from pathlib import Path
from typing import Dict, List

# Import 매핑 테이블
IMPORT_MAPPINGS = {
    "from mysingle.base import": "from mysingle.core.base import",
    "from mysingle.base.": "from mysingle.core.base.",
    "import mysingle.base": "import mysingle.core.base",
    "from mysingle.logging import": "from mysingle.core.logging import",
    "from mysingle.logging.": "from mysingle.core.logging.",
    "import mysingle.logging": "import mysingle.core.logging",
    "from mysingle.metrics import": "from mysingle.core.metrics import",
    "from mysingle.metrics.": "from mysingle.core.metrics.",
    "import mysingle.metrics": "import mysingle.core.metrics",
    "from mysingle.health import": "from mysingle.core.health import",
    "from mysingle.health.": "from mysingle.core.health.",
    "import mysingle.health": "import mysingle.core.health",
    "from mysingle.email import": "from mysingle.core.email import",
    "from mysingle.email.": "from mysingle.core.email.",
    "import mysingle.email": "import mysingle.core.email",
    "from mysingle.audit import": "from mysingle.core.audit import",
    "from mysingle.audit.": "from mysingle.core.audit.",
    "import mysingle.audit": "import mysingle.core.audit",
}


def update_file_imports(file_path: Path) -> int:
    """파일의 import 구문을 업데이트합니다."""
    content = file_path.read_text(encoding="utf-8")
    original_content = content
    changes = 0

    for old_import, new_import in IMPORT_MAPPINGS.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            changes += 1

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        return changes

    return 0


def find_python_files(root_dir: Path, exclude_dirs: List[str]) -> List[Path]:
    """Python 파일 목록을 찾습니다."""
    python_files = []

    for py_file in root_dir.rglob("*.py"):
        # 제외 디렉터리 체크
        if any(excl in str(py_file) for excl in exclude_dirs):
            continue
        python_files.append(py_file)

    return python_files


def main():
    # quant-pack 루트 찾기
    script_dir = Path(__file__).parent
    package_root = script_dir.parent.parent
    src_dir = package_root / "src" / "mysingle"

    print("=== Phase 0: Update Internal Imports ===")
    print(f"Package root: {package_root}")
    print(f"Source dir: {src_dir}")
    print()

    # mysingle 패키지 내부 파일 수정
    exclude_dirs = [".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "logs"]
    python_files = find_python_files(src_dir, exclude_dirs)

    print(f"Found {len(python_files)} Python files in mysingle package")

    total_changes = 0
    updated_files = []

    for py_file in python_files:
        changes = update_file_imports(py_file)
        if changes > 0:
            total_changes += changes
            updated_files.append(py_file)
            print(f"  ✓ {py_file.relative_to(package_root)} ({changes} changes)")

    print()
    print(f"=== Summary ===")
    print(f"Updated {len(updated_files)} files")
    print(f"Total {total_changes} import statements changed")
    print()
    print("Next: Update __init__.py exports")


if __name__ == "__main__":
    main()
