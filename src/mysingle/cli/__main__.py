"""
MySingle CLI - 통합 명령줄 도구.

현재 제공 기능:
- 버전 관리
- 서비스 스캐폴딩
- Proto 관리

향후 확장: 패키지 관리 등
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mysingle.cli.utils import console, print_error, print_header, print_info


def show_interactive_menu() -> int:
    """대화형 메뉴를 표시하고 사용자 선택을 처리합니다."""
    from rich.prompt import Prompt

    print_header("🚀 MySingle CLI")

    console.print("[cyan]사용 가능한 명령:[/cyan]\n")
    console.print("  [green]1.[/green] version    - 패키지 버전 관리")
    console.print("  [green]3.[/green] scaffold   - 서비스 스캐폴딩")
    console.print("  [green]4.[/green] proto      - Proto 파일 관리")
    console.print("  [green]5.[/green] help       - 도움말 표시")
    console.print("  [green]q.[/green] quit       - 종료\n")

    choice = Prompt.ask(
        "명령을 선택하세요", choices=["1", "2", "3", "4", "5", "q"], default="q"
    )

    if choice == "q":
        print_info("종료합니다.")
        return 0
    elif choice == "1":
        # Version subcommand interactive mode
        from .core import version as version_cmd

        return version_cmd.execute_interactive()
    elif choice == "2":
        # Submodule management
        from rich.prompt import Prompt

        from .submodule.commands import (
            execute_add_interactive,
            execute_update_interactive,
            status_submodule,
            sync_submodule,
        )

        console.print("\n[bold]Submodule 관리[/bold]\n")
        console.print("  [green]1.[/green] add     - MySingle을 submodule로 추가")
        console.print("  [green]2.[/green] status  - Submodule 상태 확인")
        console.print("  [green]3.[/green] update  - Submodule 업데이트")
        console.print("  [green]4.[/green] sync    - 변경사항 PR 준비\n")

        sub_choice = Prompt.ask(
            "명령을 선택하세요", choices=["1", "2", "3", "4"], default="2"
        )

        if sub_choice == "1":
            return execute_add_interactive()
        elif sub_choice == "2":
            return status_submodule()
        elif sub_choice == "3":
            return execute_update_interactive()
        elif sub_choice == "4":
            return sync_submodule()

    elif choice == "3":
        # Scaffold subcommand
        from .scaffold.commands import (
            execute_interactive as execute_scaffold_interactive,
        )

        return execute_scaffold_interactive(services_dir=Path.cwd() / "services")
    elif choice == "4":
        # Proto subcommand - redirect to mysingle-proto
        print_info("Proto 관리는 'mysingle-proto' 명령을 사용하세요.")
        console.print("\n예시:")
        console.print("  mysingle-proto init")
        console.print("  mysingle-proto generate")
        console.print("  mysingle-proto status\n")
        return 0
    elif choice == "5":
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

    # Submodule command
    from .submodule import commands as submodule_cmd

    submodule_parser = subparsers.add_parser(
        "submodule",
        help="Git Submodule 관리",
        description="MySingle 패키지를 submodule로 관리합니다",
    )
    submodule_subparsers = submodule_parser.add_subparsers(
        dest="submodule_command",
        help="Submodule 명령",
    )

    # submodule add
    add_parser = submodule_subparsers.add_parser(
        "add",
        help="MySingle을 submodule로 추가",
    )
    submodule_cmd.setup_add_parser(add_parser)

    # submodule status
    submodule_subparsers.add_parser(
        "status",
        help="Submodule 상태 확인",
    )

    # submodule update
    update_parser = submodule_subparsers.add_parser(
        "update",
        help="Submodule 업데이트",
    )
    submodule_cmd.setup_update_parser(update_parser)

    # submodule sync
    submodule_subparsers.add_parser(
        "sync",
        help="로컬 변경사항 PR 준비",
    )

    # Scaffold command
    from .scaffold import commands as scaffold_cmd

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="서비스 스캐폴딩",
        description="표준화된 마이크로서비스 구조를 생성합니다",
    )
    scaffold_cmd.setup_parser(scaffold_parser)

    # Parse arguments
    args = parser.parse_args(argv)

    if not args.command:
        return show_interactive_menu()

    # Execute command
    if args.command == "version":
        return version_cmd.execute(args)
    elif args.command == "submodule":
        if not args.submodule_command:
            # Interactive mode
            return show_interactive_menu()

        if args.submodule_command == "add":
            return submodule_cmd.execute_add(args)
        elif args.submodule_command == "status":
            return submodule_cmd.execute_status(args)
        elif args.submodule_command == "update":
            return submodule_cmd.execute_update(args)
        elif args.submodule_command == "sync":
            return submodule_cmd.execute_sync(args)
    elif args.command == "scaffold":
        from .scaffold import commands as scaffold_cmd

        return scaffold_cmd.execute(args)

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
