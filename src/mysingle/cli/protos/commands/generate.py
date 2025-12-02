"""
Generate 명령 - Buf를 사용하여 Python gRPC 스텁 생성.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from ...utils import ask_confirm, print_success
from ..models import ProtoConfig
from ..utils import Color, LogLevel, colorize, log, log_header


def ensure_file_exists(path: Path, description: str) -> None:
    """필수 파일 존재 확인"""
    if not path.exists():
        raise SystemExit(f"필수 파일 누락: {description} ({path})")


def buf_generate(config: ProtoConfig) -> None:
    """Buf를 사용하여 코드 생성"""
    ensure_file_exists(config.buf_template, "buf.gen.yaml 템플릿")

    log("Buf를 사용하여 코드 생성 중...", LogLevel.STEP)

    try:
        # protoc_builtin 방식으로 시도
        subprocess.run(
            [
                "buf",
                "generate",
                "protos",
                "--template",
                "protos/buf.gen.yaml",
            ],
            cwd=config.repo_root,
            check=True,
        )
        log("코드 생성 완료", LogLevel.SUCCESS)
    except subprocess.CalledProcessError as e:
        # buf 실패시 직접 protoc 사용
        log(f"Buf 생성 실패, protoc으로 fallback 중...: {e}", LogLevel.WARNING)
        try:
            _protoc_generate(config)
            log("코드 생성 완료 (protoc)", LogLevel.SUCCESS)
        except Exception as protoc_err:
            log(f"코드 생성 실패: {protoc_err}", LogLevel.ERROR)
            raise SystemExit(1) from protoc_err
    except FileNotFoundError:
        log("Buf가 설치되어 있지 않습니다. protoc으로 시도합니다...", LogLevel.WARNING)
        try:
            _protoc_generate(config)
            log("코드 생성 완료 (protoc)", LogLevel.SUCCESS)
        except Exception as e:
            log(f"코드 생성 실패: {e}", LogLevel.ERROR)
            log("Buf 설치 방법: https://buf.build/docs/installation", LogLevel.INFO)
            raise SystemExit(1)


def _protoc_generate(config: ProtoConfig) -> None:
    """protoc을 직접 사용하여 코드 생성"""
    import sys

    from grpc_tools import protoc

    protos_dir = config.repo_root / "protos"
    output_dir = config.generated_root

    # proto 파일 찾기
    proto_files = list(protos_dir.rglob("*.proto"))
    if not proto_files:
        raise RuntimeError("proto 파일을 찾을 수 없습니다")

    log(f"발견된 proto 파일: {len(proto_files)}개", LogLevel.INFO)

    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)

    # grpc_tools에 포함된 well-known types 경로 찾기
    import grpc_tools

    grpc_tools_path = Path(grpc_tools.__file__).parent / "_proto"

    # protoc 실행
    for proto_file in proto_files:
        rel_path = proto_file.relative_to(protos_dir)
        log(f"처리 중: {rel_path}", LogLevel.DEBUG)

        # protoc 명령 구성
        args = [
            sys.argv[0],  # protoc 호환을 위해
            f"--proto_path={protos_dir}",
            f"--proto_path={grpc_tools_path}",  # well-known types 경로 추가
            f"--python_out={output_dir}",
            f"--pyi_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            str(proto_file),
        ]

        # grpc_tools.protoc 실행
        result = protoc.main(args)
        if result != 0:
            raise RuntimeError(f"protoc failed for {rel_path} with code {result}")


def rewrite_generated_imports(
    generated_dir: Path, package_name: str = "mysingle"
) -> list[Path]:
    """생성된 파일의 import 경로 수정"""
    if not generated_dir.exists():
        return []

    log("생성된 파일의 import 경로 수정 중...", LogLevel.STEP)

    # .py 파일과 .pyi 타입 스텁 파일 모두 처리
    patterns = ("*_pb2.py", "*_pb2_grpc.py", "*_pb2.pyi", "*_pb2_grpc.pyi")
    replacements = [
        # Pattern 1: from protos.xxx -> from mysingle.protos.xxx
        (re.compile(r"from protos\."), f"from {package_name}.protos."),
        # Pattern 2: import protos.xxx -> import mysingle.protos.xxx
        (re.compile(r"import protos\."), f"import {package_name}.protos."),
        # Pattern 3: from common import xxx -> from mysingle.protos.common import xxx
        (
            re.compile(r"^from common import ", re.MULTILINE),
            f"from {package_name}.protos.common import ",
        ),
        # Pattern 4: from services.xxx import -> from mysingle.protos.services.xxx import
        (
            re.compile(r"^from services\.", re.MULTILINE),
            f"from {package_name}.protos.services.",
        ),
    ]

    modified: list[Path] = []

    for pattern in patterns:
        for file_path in generated_dir.rglob(pattern):
            original = file_path.read_text(encoding="utf-8")
            updated = original

            for regex, repl in replacements:
                updated = regex.sub(repl, updated)

            if updated != original:
                file_path.write_text(updated, encoding="utf-8")
                modified.append(file_path)
                log(
                    f"수정: {colorize(str(file_path.relative_to(generated_dir)), Color.CYAN)}",
                    LogLevel.DEBUG,
                )

    if modified:
        log(
            f"총 {colorize(str(len(modified)), Color.GREEN, bold=True)}개 파일 import 수정 완료",
            LogLevel.SUCCESS,
        )
    else:
        log("import 수정이 필요한 파일 없음", LogLevel.INFO)

    return modified


def ensure_init_files(generated_dir: Path) -> list[Path]:
    """생성된 디렉토리에 __init__.py 파일 생성"""
    if not generated_dir.exists():
        return []

    log("__init__.py 파일 생성 중...", LogLevel.STEP)

    created: list[Path] = []

    # protos 디렉토리의 모든 하위 디렉토리에 __init__.py 생성
    for dirpath in [generated_dir] + list(generated_dir.rglob("*/")):
        if dirpath.is_dir():
            init_file = dirpath / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                created.append(init_file)
                log(
                    f"생성: {colorize(str(init_file.relative_to(generated_dir.parent)), Color.CYAN)}",
                    LogLevel.DEBUG,
                )

    if created:
        log(
            f"총 {colorize(str(len(created)), Color.GREEN, bold=True)}개 __init__.py 파일 생성 완료",
            LogLevel.SUCCESS,
        )
    else:
        log("__init__.py 파일 생성 불필요", LogLevel.INFO)

    return created


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Generate 명령 실행"""
    log_header("Proto 코드 생성")

    # 1. Buf 코드 생성
    buf_generate(config)

    # 2. Import 경로 수정
    if not args.skip_rewrite:
        # generated_root는 이미 src/mysingle/protos를 가리킴
        rewrite_generated_imports(config.generated_root, "mysingle")

    # 3. __init__.py 파일 생성
    if not args.skip_init:
        ensure_init_files(config.generated_root)

    log("\n✅ 모든 작업 완료!", LogLevel.SUCCESS)

    return 0


def execute_interactive(config: ProtoConfig) -> int:
    """대화형 모드로 generate 명령 실행"""
    log_header("Python gRPC 스텁 생성")

    print_success("Proto 파일로부터 Python 코드를 생성합니다.")

    if not ask_confirm("계속하시겠습니까?", default=True):
        log("취소되었습니다.", LogLevel.INFO)
        return 0

    # 기본값으로 실행
    args = argparse.Namespace(skip_rewrite=False, skip_init=False)
    return execute(args, config)


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Generate 명령 파서 설정"""
    parser.add_argument(
        "--skip-rewrite",
        action="store_true",
        help="import 경로 수정 단계 건너뛰기",
    )
    parser.add_argument(
        "--skip-init",
        action="store_true",
        help="__init__.py 파일 생성 단계 건너뛰기",
    )
