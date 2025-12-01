"""
Init 명령 - mysingle 패키지 Proto 초기화.

통합 구조에서는 더 이상 submodule이 아닌 단일 패키지로 관리됩니다.
"""

from __future__ import annotations

import argparse
import subprocess

from ..models import ProtoConfig
from ..utils import Color, LogLevel, colorize, log, log_header


def execute(args: argparse.Namespace, config: ProtoConfig) -> int:
    """Init 명령 실행"""
    log_header("MySingle Proto 패키지 초기화")

    # Git 저장소 확인
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=config.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            log(
                f"Git 저장소 확인: {colorize(str(config.repo_root), Color.BRIGHT_GREEN)}",
                LogLevel.SUCCESS,
            )
        else:
            log("Git 저장소가 아닙니다.", LogLevel.ERROR)
            return 1
    except FileNotFoundError:
        log("Git이 설치되어 있지 않습니다.", LogLevel.ERROR)
        return 1

    # 브랜치 확인
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=config.repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    current_branch = result.stdout.strip()
    log(f"현재 브랜치: {colorize(current_branch, Color.BRIGHT_GREEN)}", LogLevel.INFO)

    # 원격 저장소 확인
    result = subprocess.run(
        ["git", "remote", "-v"],
        cwd=config.repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 and result.stdout:
        log("원격 저장소:", LogLevel.INFO)
        for line in result.stdout.strip().split("\n"):
            if "github.com/Br0therDan/mysingle-pack" in line:
                print(f"  {colorize(line, Color.GREEN)}")
            else:
                print(f"  {line}")
    else:
        log("원격 저장소가 설정되어 있지 않습니다.", LogLevel.WARNING)

    # Buf 설치 확인
    try:
        result = subprocess.run(
            ["buf", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            log(f"Buf 설치 확인: {colorize(version, Color.GREEN)}", LogLevel.SUCCESS)
        else:
            log("Buf가 설치되어 있지 않습니다.", LogLevel.WARNING)
            log("설치 방법: https://buf.build/docs/installation", LogLevel.INFO)
            return 1
    except FileNotFoundError:
        log("Buf가 설치되어 있지 않습니다.", LogLevel.ERROR)
        log("설치 방법: https://buf.build/docs/installation", LogLevel.INFO)
        return 1

    # 필수 디렉터리 확인
    directories = [
        ("Proto 원본", config.proto_root),
        ("Proto 생성", config.generated_root),
    ]

    log("\n필수 디렉터리 확인:", LogLevel.INFO)
    all_exist = True
    for name, path in directories:
        if path.exists():
            log(f"  ✅ {name}: {path}", LogLevel.SUCCESS)
        else:
            log(f"  ❌ {name}: {path} (없음)", LogLevel.ERROR)
            all_exist = False

    if not all_exist:
        log("\n필수 디렉터리가 존재하지 않습니다.", LogLevel.ERROR)
        return 1

    # buf.yaml 확인
    buf_yaml = config.proto_root / "buf.yaml"
    buf_gen_yaml = config.proto_root / "buf.gen.yaml"

    log("\nBuf 설정 파일 확인:", LogLevel.INFO)
    if buf_yaml.exists():
        log(f"  ✅ buf.yaml: {buf_yaml}", LogLevel.SUCCESS)
    else:
        log(f"  ❌ buf.yaml: {buf_yaml} (없음)", LogLevel.ERROR)
        all_exist = False

    if buf_gen_yaml.exists():
        log(f"  ✅ buf.gen.yaml: {buf_gen_yaml}", LogLevel.SUCCESS)
    else:
        log(f"  ❌ buf.gen.yaml: {buf_gen_yaml} (없음)", LogLevel.ERROR)
        all_exist = False

    if not all_exist:
        log("\nBuf 설정 파일이 존재하지 않습니다.", LogLevel.ERROR)
        return 1

    # 패키지 정보 출력
    log("\n" + "=" * 60, LogLevel.INFO)
    log("📦 MySingle 통합 패키지 정보", LogLevel.INFO)
    log(f"  - 저장소: {config.repo_root}", LogLevel.INFO)
    log(f"  - Proto 원본: {config.proto_root}", LogLevel.INFO)
    log(f"  - Proto 생성: {config.generated_root}", LogLevel.INFO)
    log("=" * 60, LogLevel.INFO)

    log("\n✅ 초기화 완료!", LogLevel.SUCCESS)
    log(
        f"\n다음 명령으로 상태를 확인하세요: {colorize('mysingle-proto status', Color.BRIGHT_YELLOW)}",
        LogLevel.INFO,
    )
    log(
        f"Proto 생성: {colorize('mysingle-proto generate', Color.BRIGHT_YELLOW)}",
        LogLevel.INFO,
    )

    return 0


def execute_interactive(config: ProtoConfig) -> int:
    """대화형 모드로 init 명령 실행"""
    log_header("MySingle Proto 패키지 초기화")

    # 기본 실행 (--check-only 없이)
    args = argparse.Namespace(check_only=False)
    return execute(args, config)


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Init 명령 파서 설정"""
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="초기화 없이 현재 상태만 확인",
    )
