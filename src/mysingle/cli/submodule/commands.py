"""MySingle 패키지를 Git Submodule로 관리하는 명령어들."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from mysingle.cli.utils import (
    ask_choice,
    ask_confirm,
    ask_text,
    console,
    print_error,
    print_info,
    print_success,
    print_warning,
)

MYSINGLE_REPO_URL = "https://github.com/Br0therDan/mysingle-pack.git"
DEFAULT_SUBMODULE_PATH = "libs/mysingle"


def run_git(
    args: list[str], cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Git 명령 실행"""
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def is_git_repo(path: Path = Path.cwd()) -> bool:
    """Git 저장소인지 확인"""
    try:
        run_git(["rev-parse", "--git-dir"], cwd=path)
        return True
    except subprocess.CalledProcessError:
        return False


def get_submodule_path() -> Path | None:
    """현재 저장소에서 mysingle submodule 경로 찾기"""
    try:
        result = run_git(["config", "--file", ".gitmodules", "--get-regexp", "path"])
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            # submodule.libs/mysingle.path libs/mysingle
            parts = line.split()
            if len(parts) >= 2:
                path = Path(parts[1])
                if path.name == "mysingle" or "mysingle" in str(path):
                    return path
    except subprocess.CalledProcessError:
        pass
    return None


def add_submodule(
    path: str = DEFAULT_SUBMODULE_PATH,
    branch: str = "main",
    force: bool = False,
) -> int:
    """MySingle 패키지를 submodule로 추가

    Args:
        path: submodule 경로 (기본: libs/mysingle)
        branch: 브랜치 (기본: main)
        force: 기존 디렉토리 덮어쓰기

    Returns:
        종료 코드
    """
    cwd = Path.cwd()

    # Git 저장소 확인
    if not is_git_repo(cwd):
        print_error("현재 디렉토리가 Git 저장소가 아닙니다.")
        return 1

    submodule_path = Path(path)

    # 이미 존재하는지 확인
    existing_path = get_submodule_path()
    if existing_path:
        print_warning(f"MySingle submodule이 이미 존재합니다: {existing_path}")
        if not force:
            print_info("강제로 재설정하려면 --force 옵션을 사용하세요.")
            return 1

    # 디렉토리 존재 확인
    if submodule_path.exists() and not force:
        print_error(f"디렉토리가 이미 존재합니다: {submodule_path}")
        print_info("강제로 덮어쓰려면 --force 옵션을 사용하세요.")
        return 1

    try:
        # Submodule 추가
        console.print("\n[bold]MySingle 패키지를 submodule로 추가합니다...[/bold]")
        console.print(f"  저장소: [cyan]{MYSINGLE_REPO_URL}[/cyan]")
        console.print(f"  경로: [cyan]{path}[/cyan]")
        console.print(f"  브랜치: [cyan]{branch}[/cyan]\n")

        cmd = ["submodule", "add", "-b", branch, MYSINGLE_REPO_URL, path]
        if force:
            cmd.insert(2, "--force")

        run_git(cmd, cwd=cwd)
        print_success(f"Submodule 추가 완료: {path}")

        # Submodule 초기화 및 업데이트
        run_git(["submodule", "init"], cwd=cwd)
        run_git(["submodule", "update", "--remote", path], cwd=cwd)
        print_success("Submodule 초기화 완료")

        # .gitmodules 정보 표시
        console.print("\n[bold].gitmodules 설정:[/bold]")
        gitmodules = cwd / ".gitmodules"
        if gitmodules.exists():
            with open(gitmodules) as f:
                console.print(f.read())

        # 다음 단계 안내
        console.print(
            "\n[bold green]✅ MySingle 패키지가 submodule로 추가되었습니다![/bold green]"
        )
        console.print("\n[bold]다음 단계:[/bold]")
        console.print(
            f"  1. 변경사항 커밋: [yellow]git add {path} .gitmodules && git commit -m 'chore: add mysingle submodule'[/yellow]"
        )
        console.print("  2. 상태 확인: [yellow]mysingle submodule status[/yellow]")
        console.print(
            f"  3. Proto 생성: [yellow]cd {path} && mysingle-proto generate[/yellow]"
        )

        return 0

    except subprocess.CalledProcessError as e:
        print_error(f"Submodule 추가 실패: {e.stderr}")
        return 1


def status_submodule() -> int:
    """MySingle submodule 상태 확인"""
    cwd = Path.cwd()

    if not is_git_repo(cwd):
        print_error("현재 디렉토리가 Git 저장소가 아닙니다.")
        return 1

    # Submodule 경로 찾기
    submodule_path = get_submodule_path()
    if not submodule_path:
        print_warning("MySingle submodule을 찾을 수 없습니다.")
        console.print("\n[bold]Submodule 추가 방법:[/bold]")
        console.print("  [yellow]mysingle submodule add[/yellow]\n")
        return 1

    console.print("\n[bold]MySingle Submodule 상태[/bold]\n")

    # Submodule 상태
    try:
        result = run_git(["submodule", "status", str(submodule_path)])
        console.print(f"[cyan]{result.stdout.strip()}[/cyan]\n")
    except subprocess.CalledProcessError as e:
        print_error(f"상태 확인 실패: {e.stderr}")
        return 1

    # 현재 브랜치
    try:
        result = run_git(["branch", "--show-current"], cwd=submodule_path)
        branch = result.stdout.strip()
        console.print(f"📍 현재 브랜치: [green]{branch}[/green]")
    except subprocess.CalledProcessError:
        console.print("📍 현재 브랜치: [yellow]detached HEAD[/yellow]")

    # 버전 확인
    full_path = cwd / submodule_path
    pyproject = full_path / "pyproject.toml"
    if pyproject.exists():
        import tomllib

        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
            version = data.get("project", {}).get("version", "unknown")
            console.print(f"📦 MySingle 버전: [cyan]{version}[/cyan]")

    # 리모트 상태
    try:
        result = run_git(["remote", "-v"], cwd=submodule_path)
        if result.stdout:
            console.print("\n🔗 리모트 저장소:")
            for line in result.stdout.strip().split("\n"):
                if "(fetch)" in line:
                    console.print(f"  {line}")
    except subprocess.CalledProcessError:
        pass

    # 변경사항 확인
    try:
        result = run_git(["status", "--short"], cwd=submodule_path, check=False)
        if result.stdout.strip():
            console.print("\n⚠️  [yellow]로컬 변경사항 있음:[/yellow]")
            console.print(result.stdout)
        else:
            console.print("\n✅ [green]변경사항 없음[/green]")
    except subprocess.CalledProcessError:
        pass

    # 업스트림 커밋 차이
    try:
        run_git(["fetch"], cwd=submodule_path, check=False)
        result = run_git(
            ["rev-list", "--left-right", "--count", "HEAD...@{u}"],
            cwd=submodule_path,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            ahead, behind = result.stdout.strip().split()
            if int(ahead) > 0 or int(behind) > 0:
                console.print("\n📊 업스트림 비교:")
                console.print(f"  로컬 앞섬: {ahead} 커밋")
                console.print(f"  원격 앞섬: {behind} 커밋")
    except subprocess.CalledProcessError:
        pass

    return 0


def update_submodule(remote: bool = True) -> int:
    """MySingle submodule 업데이트

    Args:
        remote: 원격 저장소에서 최신 변경사항 가져오기

    Returns:
        종료 코드
    """
    cwd = Path.cwd()

    if not is_git_repo(cwd):
        print_error("현재 디렉토리가 Git 저장소가 아닙니다.")
        return 1

    submodule_path = get_submodule_path()
    if not submodule_path:
        print_error("MySingle submodule을 찾을 수 없습니다.")
        return 1

    try:
        console.print("\n[bold]MySingle submodule 업데이트 중...[/bold]\n")

        if remote:
            # 원격에서 최신 변경사항 가져오기
            run_git(["submodule", "update", "--remote", str(submodule_path)])
            print_success(f"원격 저장소에서 업데이트 완료: {submodule_path}")
        else:
            # 부모 저장소에 기록된 커밋으로 업데이트
            run_git(["submodule", "update", str(submodule_path)])
            print_success(f"기록된 커밋으로 업데이트 완료: {submodule_path}")

        # 업데이트 후 상태 표시
        return status_submodule()

    except subprocess.CalledProcessError as e:
        print_error(f"업데이트 실패: {e.stderr}")
        return 1


def sync_submodule() -> int:
    """로컬 변경사항을 MySingle 저장소에 PR로 제출하기 위한 준비

    Returns:
        종료 코드
    """
    cwd = Path.cwd()

    if not is_git_repo(cwd):
        print_error("현재 디렉토리가 Git 저장소가 아닙니다.")
        return 1

    submodule_path = get_submodule_path()
    if not submodule_path:
        print_error("MySingle submodule을 찾을 수 없습니다.")
        return 1

    full_path = cwd / submodule_path

    # 변경사항 확인
    try:
        result = run_git(["status", "--short"], cwd=full_path, check=False)
        if not result.stdout.strip():
            print_info("변경사항이 없습니다.")
            return 0

        console.print("\n[bold]로컬 변경사항:[/bold]\n")
        console.print(result.stdout)

        # 브랜치 확인
        result = run_git(["branch", "--show-current"], cwd=full_path, check=False)
        current_branch = result.stdout.strip()

        if current_branch == "main":
            print_warning("main 브랜치에서 작업 중입니다.")
            if ask_confirm("새 브랜치를 생성하시겠습니까?", default=True):
                branch_name = ask_text(
                    "브랜치 이름을 입력하세요",
                    default=f"feature/update-from-{Path.cwd().name}",
                )
                run_git(["checkout", "-b", branch_name], cwd=full_path)
                print_success(f"새 브랜치 생성: {branch_name}")
                current_branch = branch_name
            else:
                print_info("취소되었습니다.")
                return 1

        # 커밋
        if ask_confirm("변경사항을 커밋하시겠습니까?", default=True):
            run_git(["add", "-A"], cwd=full_path)

            commit_msg = ask_text(
                "커밋 메시지를 입력하세요",
                default=f"feat: update from {Path.cwd().name}",
            )

            run_git(["commit", "-m", commit_msg], cwd=full_path)
            print_success("커밋 완료")

            # Fork 확인
            result = run_git(["remote", "-v"], cwd=full_path, check=False)
            has_fork = (
                "origin" in result.stdout
                and "Br0therDan/mysingle-pack" not in result.stdout
            )

            if not has_fork:
                console.print(
                    "\n[bold yellow]⚠️  Fork된 저장소가 설정되지 않았습니다.[/bold yellow]"
                )
                console.print("\n[bold]Fork 설정 방법:[/bold]")
                console.print("  1. GitHub에서 mysingle-pack을 fork하세요")
                console.print(f"  2. [yellow]cd {submodule_path}[/yellow]")
                console.print(
                    "  3. [yellow]git remote set-url origin https://github.com/YOUR_USERNAME/mysingle-pack.git[/yellow]"
                )
                console.print(
                    "  4. [yellow]git remote add upstream https://github.com/Br0therDan/mysingle-pack.git[/yellow]"
                )
                return 1

            # Push
            if ask_confirm(
                f"'{current_branch}' 브랜치를 origin에 푸시하시겠습니까?", default=True
            ):
                run_git(["push", "origin", current_branch], cwd=full_path)
                print_success("푸시 완료")

                console.print("\n[bold green]✅ 동기화 완료![/bold green]")
                console.print("\n[bold]다음 단계:[/bold]")
                console.print("  1. GitHub에서 PR 생성")
                console.print(
                    "  2. [yellow]https://github.com/Br0therDan/mysingle-pack/compare[/yellow]"
                )
                console.print(f"  3. base: main ← compare: {current_branch}")

        return 0

    except subprocess.CalledProcessError as e:
        print_error(f"동기화 실패: {e.stderr}")
        return 1


def setup_add_parser(parser: argparse.ArgumentParser) -> None:
    """Submodule add 명령 파서 설정"""
    parser.add_argument(
        "--path",
        default=DEFAULT_SUBMODULE_PATH,
        help=f"Submodule 경로 (기본: {DEFAULT_SUBMODULE_PATH})",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="브랜치 (기본: main)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="기존 디렉토리 덮어쓰기",
    )


def setup_update_parser(parser: argparse.ArgumentParser) -> None:
    """Submodule update 명령 파서 설정"""
    parser.add_argument(
        "--no-remote",
        action="store_true",
        help="원격 저장소에서 가져오지 않고 부모 저장소에 기록된 커밋으로 업데이트",
    )


def execute_add(args: argparse.Namespace) -> int:
    """Add 명령 실행"""
    return add_submodule(
        path=args.path,
        branch=args.branch,
        force=args.force,
    )


def execute_status(args: argparse.Namespace) -> int:
    """Status 명령 실행"""
    return status_submodule()


def execute_update(args: argparse.Namespace) -> int:
    """Update 명령 실행"""
    return update_submodule(remote=not args.no_remote)


def execute_sync(args: argparse.Namespace) -> int:
    """Sync 명령 실행"""
    return sync_submodule()


# Interactive 모드
def execute_add_interactive() -> int:
    """대화형 모드로 submodule 추가"""
    console.print("\n[bold]MySingle 패키지 Submodule 추가[/bold]\n")

    path = ask_text("Submodule 경로를 입력하세요", default=DEFAULT_SUBMODULE_PATH)
    branch = ask_text("브랜치를 선택하세요", default="main")

    force = False
    if Path(path).exists():
        force = ask_confirm(
            "디렉토리가 이미 존재합니다. 덮어쓰시겠습니까?", default=False
        )
        if not force:
            print_info("취소되었습니다.")
            return 1

    return add_submodule(path=path, branch=branch, force=force)


def execute_update_interactive() -> int:
    """대화형 모드로 submodule 업데이트"""
    console.print("\n[bold]MySingle Submodule 업데이트[/bold]\n")

    update_type = ask_choice(
        "업데이트 방식을 선택하세요",
        ["remote", "recorded", "cancel"],
        default="remote",
    )

    if update_type == "cancel":
        print_info("취소되었습니다.")
        return 0

    return update_submodule(remote=(update_type == "remote"))
