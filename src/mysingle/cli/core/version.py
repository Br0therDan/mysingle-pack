"""버전 관리 명령."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from mysingle.cli.utils import (
    ask_choice,
    ask_confirm,
    console,
    print_error,
    print_info,
    print_success,
    print_warning,
)


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    prerelease: str | None = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            return f"{base}-{self.prerelease}"
        return base

    @classmethod
    def parse(cls, s: str) -> "Version":
        # Match version with optional prerelease (e.g., 2.0.0-alpha)
        m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?", s.strip())
        if not m:
            raise ValueError(f"Invalid version: {s}")
        return cls(
            int(m.group(1)),
            int(m.group(2)),
            int(m.group(3)),
            m.group(4) if m.group(4) else None,
        )

    def bump(self, kind: str) -> "Version":
        if kind == "major":
            return Version(self.major + 1, 0, 0)
        if kind == "minor":
            return Version(self.major, self.minor + 1, 0)
        if kind == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError(f"Unknown bump kind: {kind}")


def find_pyproject() -> Path:
    """현재 디렉토리 또는 상위 디렉토리에서 pyproject.toml을 찾습니다."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            return pyproject
    raise FileNotFoundError("pyproject.toml을 찾을 수 없습니다")


def read_current_version(pyproject_path: Path) -> Version:
    """pyproject.toml에서 버전을 읽습니다."""
    import tomllib

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    try:
        v = data["project"]["version"]
        return Version.parse(v)
    except KeyError:
        with open(pyproject_path, "r", encoding="utf-8") as fr:
            raw = fr.read()
        m = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"\s*$', raw)
        if m:
            return Version.parse(m.group(1))
        return Version(0, 0, 0)


def get_current_version() -> Version:
    """pyproject.toml에서 현재 버전을 가져옵니다.

    Returns:
        Version: 현재 버전

    Raises:
        FileNotFoundError: pyproject.toml을 찾을 수 없는 경우
    """
    pyproject_path = find_pyproject()
    return read_current_version(pyproject_path)


def write_version(pyproject_path: Path, new_version: Version) -> None:
    """pyproject.toml에 새 버전을 작성합니다."""
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r'(?m)^(\s*version\s*=\s*")([^"]+)(")\s*$')
    if pattern.search(content):
        content = pattern.sub(
            lambda m: f"{m.group(1)}{new_version}{m.group(3)}", content
        )
    else:
        # Insert after name line in [project] section
        content = re.sub(
            r'(?m)^(\s*name\s*=\s*".*"\s*\n)',
            f'\\1version = "{new_version}"\n',
            content,
            count=1,
        )

    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(content)


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Git 명령을 실행합니다."""
    return subprocess.run(["git"] + args, check=check, capture_output=True, text=True)


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """버전 명령 파서를 설정합니다."""
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch", "show", "auto"],
        nargs="?",
        help="버전 범프 유형, 'show'로 현재 버전 표시, 또는 'auto'로 자동 분석",
    )
    parser.add_argument(
        "--custom",
        help="사용자 정의 버전 문자열 (예: 2.1.0)",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Git 커밋을 생성하지 않음",
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="Git 태그를 생성하지 않음",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="커밋과 태그를 origin에 푸시",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="변경하지 않고 분석만 수행 (auto 모드에서만 사용)",
    )


def execute_interactive() -> int:
    """대화형 모드로 버전 관리를 실행합니다."""
    try:
        pyproject_path = find_pyproject()
    except FileNotFoundError as e:
        print_error(str(e))
        return 1

    current = read_current_version(pyproject_path)
    console.print(f"\n[bold]현재 버전:[/bold] [cyan]{current}[/cyan]\n")

    # Ask for bump type
    bump_type = ask_choice(
        "버전 업데이트 유형을 선택하세요",
        ["auto", "major", "minor", "patch", "show", "cancel"],
        default="auto",
    )

    if bump_type == "cancel":
        print_info("취소되었습니다.")
        return 0

    if bump_type == "show":
        console.print(f"\n[bold green]현재 버전:[/bold green] {current}\n")
        return 0

    # Auto mode
    if bump_type == "auto":
        from .auto_version import auto_bump

        print_info("커밋 메시지를 분석하여 자동으로 버전을 결정합니다...")
        return auto_bump(dry_run=False, push=False, no_commit=False, no_tag=False)

    # Manual bump
    # Calculate new version
    new_version = current.bump(bump_type)
    console.print(
        f"\n[yellow]버전 변경:[/yellow] {current} → [green]{new_version}[/green]\n"
    )

    # Confirm
    if not ask_confirm("계속하시겠습니까?", default=True):
        print_info("취소되었습니다.")
        return 0

    # Write version
    write_version(pyproject_path, new_version)
    print_success(f"{pyproject_path.name} 업데이트 완료")

    # Ask for git operations
    try:
        run_git(["rev-parse", "--git-dir"])
        has_git = True
    except subprocess.CalledProcessError:
        has_git = False

    if has_git and ask_confirm("Git 커밋을 생성하시겠습니까?", default=True):
        try:
            run_git(["add", str(pyproject_path)])
            msg = f"chore(release): v{new_version} (bump {bump_type})"
            run_git(["commit", "-m", msg])
            print_success(f"커밋 생성 완료: {msg}")

            if ask_confirm("Git 태그를 생성하시겠습니까?", default=True):
                run_git(["tag", f"v{new_version}"])
                print_success(f"태그 생성 완료: v{new_version}")

                if ask_confirm("origin에 푸시하시겠습니까?", default=False):
                    run_git(["push", "origin", "HEAD"])
                    print_success("커밋 푸시 완료")
                    run_git(["push", "origin", f"v{new_version}"])
                    print_success("태그 푸시 완료")

        except subprocess.CalledProcessError as e:
            print_error(f"Git 작업 실패: {e.stderr}")
            return 1

    return 0


def execute(args: argparse.Namespace) -> int:
    """버전 명령을 실행합니다."""
    # If no bump_type specified, go interactive
    if not args.bump_type:
        return execute_interactive()

    # Auto mode
    if args.bump_type == "auto":
        from .auto_version import auto_bump

        return auto_bump(
            dry_run=args.dry_run,
            push=args.push,
            no_commit=args.no_commit,
            no_tag=args.no_tag,
        )

    try:
        pyproject_path = find_pyproject()
    except FileNotFoundError as e:
        print_error(str(e))
        return 1

    current = read_current_version(pyproject_path)

    if args.bump_type == "show":
        console.print(f"[bold]현재 버전:[/bold] [cyan]{current}[/cyan]")
        return 0

    # Determine new version
    if args.custom:
        try:
            new_version = Version.parse(args.custom)
        except ValueError as e:
            print_error(str(e))
            return 1
    else:
        new_version = current.bump(args.bump_type)

    console.print(
        f"[yellow]버전 변경:[/yellow] {current} → [green]{new_version}[/green]"
    )

    # Write new version
    write_version(pyproject_path, new_version)
    print_success(f"{pyproject_path.name} 업데이트 완료")

    # Git operations
    if not args.no_commit:
        try:
            # Check if git repo
            run_git(["rev-parse", "--git-dir"])

            # Add and commit
            run_git(["add", str(pyproject_path)])
            msg = f"chore(release): v{new_version} (bump {args.bump_type})"
            run_git(["commit", "-m", msg])
            print_success(f"커밋 생성 완료: {msg}")

            # Create tag
            if not args.no_tag:
                run_git(["tag", f"v{new_version}"])
                print_success(f"태그 생성 완료: v{new_version}")

            # Push
            if args.push:
                run_git(["push", "origin", "HEAD"])
                print_success("커밋 푸시 완료")
                if not args.no_tag:
                    run_git(["push", "origin", f"v{new_version}"])
                    print_success("태그 푸시 완료")

        except subprocess.CalledProcessError as e:
            print_warning(f"Git 작업 실패: {e.stderr}")
            return 1

    return 0
