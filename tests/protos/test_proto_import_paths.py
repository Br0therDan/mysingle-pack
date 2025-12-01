"""
Tests for proto generated file import paths.

Ensures all generated proto files use correct mysingle.protos.* import paths.
"""

import re
from pathlib import Path

import pytest


def get_proto_root() -> Path:
    """Get the proto root directory."""
    return Path(__file__).parent.parent.parent / "src" / "mysingle" / "protos"


def find_proto_files(pattern: str) -> list[Path]:
    """Find proto files matching the pattern."""
    proto_root = get_proto_root()
    if not proto_root.exists():
        return []
    return list(proto_root.rglob(pattern))


def check_imports_in_file(file_path: Path) -> list[str]:
    """Check for incorrect import patterns in a file.

    Returns:
        List of lines with incorrect imports
    """
    content = file_path.read_text(encoding="utf-8")

    # Patterns that should NOT exist (incorrect imports)
    bad_patterns = [
        r"^from common import ",
        r"^from services\.",
        r"^from services import ",
        r"^import common\.",
        r"^import services\.",
    ]

    incorrect_lines = []

    for line_num, line in enumerate(content.split("\n"), start=1):
        line = line.strip()
        for pattern in bad_patterns:
            if re.match(pattern, line):
                incorrect_lines.append(f"Line {line_num}: {line}")

    return incorrect_lines


class TestProtoImportPaths:
    """Test proto generated files have correct import paths."""

    def test_pb2_py_files_have_correct_imports(self):
        """Test that all *_pb2.py files use mysingle.protos.* imports."""
        pb2_files = find_proto_files("*_pb2.py")

        if not pb2_files:
            pytest.skip("No *_pb2.py files found")

        errors = {}
        for pb2_file in pb2_files:
            incorrect = check_imports_in_file(pb2_file)
            if incorrect:
                errors[str(pb2_file.relative_to(get_proto_root()))] = incorrect

        if errors:
            error_msg = "\n\n".join(
                f"{file}:\n  " + "\n  ".join(lines) for file, lines in errors.items()
            )
            pytest.fail(
                f"Found incorrect imports in {len(errors)} file(s):\n\n{error_msg}\n\n"
                f"All imports should use 'from mysingle.protos.common' or 'from mysingle.protos.services.*'"
            )

    def test_pb2_grpc_py_files_have_correct_imports(self):
        """Test that all *_pb2_grpc.py files use mysingle.protos.* imports."""
        grpc_files = find_proto_files("*_pb2_grpc.py")

        if not grpc_files:
            pytest.skip("No *_pb2_grpc.py files found")

        errors = {}
        for grpc_file in grpc_files:
            incorrect = check_imports_in_file(grpc_file)
            if incorrect:
                errors[str(grpc_file.relative_to(get_proto_root()))] = incorrect

        if errors:
            error_msg = "\n\n".join(
                f"{file}:\n  " + "\n  ".join(lines) for file, lines in errors.items()
            )
            pytest.fail(
                f"Found incorrect imports in {len(errors)} file(s):\n\n{error_msg}\n\n"
                f"All imports should use 'from mysingle.protos.common' or 'from mysingle.protos.services.*'"
            )

    def test_pyi_stub_files_have_correct_imports(self):
        """Test that all *.pyi stub files use mysingle.protos.* imports."""
        pyi_files = find_proto_files("*_pb2.pyi") + find_proto_files("*_pb2_grpc.pyi")

        if not pyi_files:
            pytest.skip("No *.pyi stub files found")

        errors = {}
        for pyi_file in pyi_files:
            incorrect = check_imports_in_file(pyi_file)
            if incorrect:
                errors[str(pyi_file.relative_to(get_proto_root()))] = incorrect

        if errors:
            error_msg = "\n\n".join(
                f"{file}:\n  " + "\n  ".join(lines) for file, lines in errors.items()
            )
            pytest.fail(
                f"Found incorrect imports in {len(errors)} file(s):\n\n{error_msg}\n\n"
                f"All imports should use 'from mysingle.protos.common' or 'from mysingle.protos.services.*'"
            )

    def test_all_proto_files_are_importable(self):
        """Test that all generated proto files can be imported."""
        proto_root = get_proto_root()

        if not proto_root.exists():
            pytest.skip("Proto root directory not found")

        # Test common protos
        try:
            from mysingle.protos.common import error_pb2, metadata_pb2, pagination_pb2

            assert error_pb2 is not None
            assert metadata_pb2 is not None
            assert pagination_pb2 is not None
        except ImportError as e:
            pytest.fail(f"Failed to import common protos: {e}")

        # Test service protos (check at least one from each service)
        service_imports = [
            ("mysingle.protos.services.genai.v1", "chatops_pb2"),
            ("mysingle.protos.services.strategy.v1", "strategy_service_pb2"),
        ]

        for module_path, module_name in service_imports:
            try:
                module = __import__(
                    f"{module_path}.{module_name}", fromlist=[module_name]
                )
                assert module is not None
            except ImportError as e:
                # Skip if service proto doesn't exist
                if "No module named" in str(e):
                    continue
                pytest.fail(f"Failed to import {module_path}.{module_name}: {e}")

    def test_no_relative_imports_in_proto_files(self):
        """Test that proto files don't use relative imports."""
        all_files = (
            find_proto_files("*_pb2.py")
            + find_proto_files("*_pb2_grpc.py")
            + find_proto_files("*_pb2.pyi")
            + find_proto_files("*_pb2_grpc.pyi")
        )

        if not all_files:
            pytest.skip("No proto files found")

        relative_import_pattern = re.compile(r"^from \. import ")
        errors = {}

        for proto_file in all_files:
            content = proto_file.read_text(encoding="utf-8")
            incorrect = []

            for line_num, line in enumerate(content.split("\n"), start=1):
                if relative_import_pattern.match(line.strip()):
                    incorrect.append(f"Line {line_num}: {line.strip()}")

            if incorrect:
                errors[str(proto_file.relative_to(get_proto_root()))] = incorrect

        if errors:
            error_msg = "\n\n".join(
                f"{file}:\n  " + "\n  ".join(lines) for file, lines in errors.items()
            )
            pytest.fail(
                f"Found relative imports in {len(errors)} file(s):\n\n{error_msg}\n\n"
                f"Proto files should use absolute imports like 'from mysingle.protos.*'"
            )
