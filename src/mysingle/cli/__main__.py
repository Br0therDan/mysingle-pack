"""
MySingle CLI - 통합 명령줄 도구.

현재 제공 기능:
- 버전 관리
- Proto 관리

향후 확장: 패키지 관리, 서비스 스캐폴딩 등
"""

from __future__ import annotations

import argparse
import sys

from .utils import console, print_error, print_header, print_info


def show_interactive_menu() -> int:
    """대화형 메뉴를 표시하고 사용자 선택을 처리합니다."""
    from rich.prompt import Prompt

    print_header("🚀 MySingle CLI")

    console.print("[cyan]사용 가능한 명령:[/cyan]\n")
    console.print("  [green]1.[/green] version  - 패키지 버전 관리")
    console.print("  [green]2.[/green] proto    - Proto 파일 관리")
    console.print("  [green]3.[/green] help     - 도움말 표시")
    console.print("  [green]q.[/green] quit     - 종료\n")

    choice = Prompt.ask("명령을 선택하세요", choices=["1", "2", "3", "q"], default="q")

    if choice == "q":
        print_info("종료합니다.")
        return 0
    elif choice == "1":
        # Version subcommand interactive mode
        from .core import version as version_cmd

        return version_cmd.execute_interactive()
    elif choice == "2":
        # Proto subcommand - redirect to mysingle-proto
        print_info("Proto 관리는 'mysingle-proto' 명령을 사용하세요.")
        console.print("\n예시:")
        console.print("  mysingle-proto init")
        console.print("  mysingle-proto generate")
        console.print("  mysingle-proto status\n")
        return 0
    elif choice == "3":
        # Show help
        main_with_args(["--help"])
        return 0

    return 0


def main_with_args(argv: list[str] | None = None) -> int:
    """명령줄 인자를 처리하는 메인 함수."""
    parser = argparse.ArgumentParser(
        prog="mysingle",
        description="MySingle 플랫폼 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령")

    # Version command
    from .core import version as version_cmd

    version_parser = subparsers.add_parser(
        "version",
        help="패키지 버전 관리",
        description="패키지 버전을 업데이트하고 릴리즈를 생성합니다",
    )
    version_cmd.setup_parser(version_parser)

    # Parse arguments
    args = parser.parse_args(argv)

    if not args.command:
        return show_interactive_menu()

    # Execute command
    if args.command == "version":
        return version_cmd.execute(args)

    return 0


def main() -> int:
    """메인 진입점."""
    try:
        return main_with_args()
    except KeyboardInterrupt:
        print_error("\n사용자에 의해 중단되었습니다.")
        return 130
    except Exception as e:
        print_error(f"예상치 못한 오류가 발생했습니다: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
