"""
Proto CLI - gRPC Proto 파일 관리 도구.

사용법:
    mysingle-proto init              # 저장소 초기화 및 submodule 구성
    mysingle-proto status            # 서비스별 proto 파일 현황
    mysingle-proto generate          # 코드 생성
    mysingle-proto validate          # Proto 파일 검증
    mysingle-proto info              # 패키지 버전 및 상태 정보
    mysingle-proto                   # 대화형 모드
    mysingle-proto --help            # 도움말
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..utils import console, print_error, print_header, print_info
from .commands import generate, info, init, status, validate
from .models import ProtoConfig
from .utils import LogLevel, log


def get_repo_root() -> Path:
    """저장소 루트 디렉터리 찾기"""
    # CLI가 패키지로 설치된 경우
    current = Path.cwd()

    # grpc-protos 디렉터리 찾기
    for parent in [current, *current.parents]:
        if (parent / "protos").exists() and (parent / "buf.yaml").exists():
            return parent

    # 찾지 못한 경우 현재 디렉터리 사용
    return current


def show_interactive_menu(config: ProtoConfig) -> int:
    """대화형 메뉴를 표시하고 사용자 선택을 처리합니다."""
    from rich.prompt import Prompt

    print_header("🔧 MySingle Proto CLI")

    console.print("[cyan]사용 가능한 명령:[/cyan]\n")
    console.print("  [green]1.[/green] init      - 저장소 초기화 및 환경 확인")
    console.print("  [green]2.[/green] status    - 서비스별 proto 파일 현황")
    console.print("  [green]3.[/green] generate  - Python gRPC 스텁 생성")
    console.print("  [green]4.[/green] validate  - Proto 파일 검증")
    console.print("  [green]5.[/green] info      - 패키지 버전 및 상태 정보")
    console.print("  [green]h.[/green] help      - 도움말 표시")
    console.print("  [green]q.[/green] quit      - 종료\n")

    choice = Prompt.ask(
        "명령을 선택하세요", choices=["1", "2", "3", "4", "5", "h", "q"], default="q"
    )

    if choice == "q":
        print_info("종료합니다.")
        return 0
    elif choice == "h":
        # Show help
        build_parser().print_help()
        return 0
    elif choice == "1":
        # init command
        return init.execute_interactive(config)
    elif choice == "2":
        # status command
        return status.execute_interactive(config)
    elif choice == "3":
        # generate command
        return generate.execute_interactive(config)
    elif choice == "4":
        # validate command
        return validate.execute_interactive(config)
    elif choice == "5":
        # info command
        import argparse

        args = argparse.Namespace()
        return info.execute(args, config)

    return 0


def build_parser() -> argparse.ArgumentParser:
    """CLI 파서 생성"""
    parser = argparse.ArgumentParser(
        prog="proto-cli",
        description="🔧 MySingle Quant - gRPC Proto 파일 관리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s init                    # 저장소 환경 확인 / Submodule 구성
  %(prog)s status                  # 서비스별 proto 현황
  %(prog)s status -v               # 상세 파일 목록 포함
  %(prog)s validate --fix          # Proto 검증 및 자동 수정
  %(prog)s generate                # 코드 생성

더 자세한 정보:
  GitHub: https://github.com/Br0therDan/grpc-protos
        """,
    )

    parser.add_argument(
        "--services-root",
        type=Path,
        help="서비스 루트 디렉터리 경로 (기본값: ../services)",
    )

    # 서브커맨드
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령")

    # init 명령
    init_parser = subparsers.add_parser(
        "init",
        help="저장소 초기화 및 환경 확인",
        description="grpc-protos 저장소를 초기화하고 필수 도구(Git, Buf) 설치를 확인합니다.",
    )
    init.setup_parser(init_parser)

    # status 명령
    status_parser = subparsers.add_parser(
        "status",
        help="서비스별 proto 파일 현황 확인",
        description="각 서비스의 proto 파일 개수와 경로를 테이블 형식으로 출력합니다.",
    )
    status.setup_parser(status_parser)

    # generate 명령
    generate_parser = subparsers.add_parser(
        "generate",
        help="Buf를 사용하여 Python gRPC 스텁 생성",
        description="proto 파일로부터 Python 코드를 생성하고 import 경로를 수정합니다.",
    )
    generate.setup_parser(generate_parser)

    # validate 명령
    validate_parser = subparsers.add_parser(
        "validate",
        help="Proto 파일 검증 (lint, format, breaking)",
        description="Buf를 사용하여 proto 파일의 린트, 포맷, Breaking change를 검사합니다.",
    )
    validate.setup_parser(validate_parser)

    # info 명령
    info_parser = subparsers.add_parser(
        "info",
        help="패키지 버전 및 상태 정보 확인",
        description="현재 mysingle 패키지 버전과 Git 상태를 확인합니다.",
    )
    info.setup_parser(info_parser)

    # TODO: 추가 명령어 구현 예정
    # - pr: Pull Request 생성 자동화
    # - diff: Proto 변경사항 시각화

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 메인 함수"""
    parser = build_parser()
    args = parser.parse_args(argv)

    # 저장소 설정
    try:
        repo_root = get_repo_root()
        config = ProtoConfig.from_repo_root(repo_root, services_root=args.services_root)
    except Exception as e:
        log(f"설정 로드 실패: {e}", LogLevel.ERROR)
        return 1

    # 명령이 지정되지 않은 경우 대화형 모드
    if not args.command:
        return show_interactive_menu(config)

    # 명령 실행
    try:
        if args.command == "init":
            return init.execute(args, config)
        elif args.command == "status":
            return status.execute(args, config)
        elif args.command == "generate":
            return generate.execute(args, config)
        elif args.command == "validate":
            return validate.execute(args, config)
        elif args.command == "info":
            return info.execute(args, config)
        else:
            log(f"알 수 없는 명령: {args.command}", LogLevel.ERROR)
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print_error("\n작업이 사용자에 의해 중단되었습니다.")
        return 130
    except Exception as e:
        print_error(f"오류 발생: {e}")
        if "--debug" in sys.argv:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
