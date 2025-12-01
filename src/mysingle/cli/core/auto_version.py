"""Conventional Commits 기반 자동 버전 관리.

Commit 메시지 분석:
- feat: → minor 버전 증가
- fix: → patch 버전 증가
- feat!: 또는 BREAKING CHANGE: → major 버전 증가
- chore:, docs:, style:, refactor:, test: → 버전 변경 없음

Proto 변경 특수 처리:
- proto: feat: → proto patch 버전 증가 (메인 버전은 유지)
- protos/ 디렉토리 변경만 있는 경우 → proto patch만 증가
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from ..utils import console, print_error, print_info, print_success
from .version import Version, find_pyproject, read_current_version, write_version


@dataclass
class CommitInfo:
    """커밋 정보"""

    sha: str
    message: str
    files: list[str]

    @property
    def is_breaking(self) -> bool:
        """Breaking change 여부"""
        return (
            "BREAKING CHANGE:" in self.message
            or "!" in self.message.split(":")[0]
            or re.match(r"^[a-z]+!:", self.message) is not None
        )

    @property
    def is_feat(self) -> bool:
        """Feature 커밋 여부"""
        return self.message.startswith("feat:")

    @property
    def is_fix(self) -> bool:
        """Fix 커밋 여부"""
        return self.message.startswith("fix:")

    @property
    def is_proto_only(self) -> bool:
        """Proto 파일만 변경되었는지 확인"""
        if not self.files:
            return False
        return all(
            f.startswith("protos/") or f.startswith("src/mysingle/protos/")
            for f in self.files
        )

    @property
    def is_proto_related(self) -> bool:
        """Proto 관련 변경 포함 여부"""
        return any(
            f.startswith("protos/") or f.startswith("src/mysingle/protos/")
            for f in self.files
        )

    @property
    def type(self) -> str:
        """커밋 타입 추출 (feat, fix, chore 등)"""
        match = re.match(r"^([a-z]+)(?:\([^)]+\))?!?:", self.message)
        return match.group(1) if match else "unknown"


def get_commits_since_tag(tag: str | None = None) -> list[CommitInfo]:
    """마지막 태그 이후의 커밋 목록 가져오기

    Args:
        tag: 시작 태그 (None이면 마지막 태그부터)

    Returns:
        커밋 정보 리스트
    """
    if tag is None:
        # Get latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # No tags yet, get all commits
            tag_ref = ""
        else:
            tag = result.stdout.strip()
            tag_ref = f"{tag}.."
    else:
        tag_ref = f"{tag}.."

    # Get commit list
    result = subprocess.run(
        ["git", "log", f"{tag_ref}HEAD", "--oneline", "--pretty=format:%H|||%s"],
        capture_output=True,
        text=True,
        check=True,
    )

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        sha, message = line.split("|||", 1)

        # Get files changed in this commit
        files_result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
            capture_output=True,
            text=True,
            check=True,
        )
        files = (
            files_result.stdout.strip().split("\n")
            if files_result.stdout.strip()
            else []
        )

        commits.append(CommitInfo(sha=sha, message=message, files=files))

    return commits


def analyze_commits(commits: list[CommitInfo]) -> dict:
    """커밋 분석하여 버전 변경 제안

    Args:
        commits: 분석할 커밋 목록

    Returns:
        분석 결과 딕셔너리
        {
            'bump_type': 'major' | 'minor' | 'patch' | 'none',
            'proto_bump': True | False,
            'breaking_changes': [...],
            'features': [...],
            'fixes': [...],
            'proto_changes': [...],
        }
    """
    result = {
        "bump_type": "none",
        "proto_bump": False,
        "breaking_changes": [],
        "features": [],
        "fixes": [],
        "proto_changes": [],
        "other_changes": [],
    }

    for commit in commits:
        # Breaking changes
        if commit.is_breaking:
            result["breaking_changes"].append(commit)
            if result["bump_type"] not in ["major"]:
                result["bump_type"] = "major"

        # Features
        elif commit.is_feat:
            result["features"].append(commit)
            if result["bump_type"] not in ["major", "minor"]:
                # Proto-only features don't bump main version
                if not commit.is_proto_only:
                    result["bump_type"] = "minor"
                else:
                    result["proto_bump"] = True

        # Fixes
        elif commit.is_fix:
            result["fixes"].append(commit)
            if result["bump_type"] == "none":
                # Proto-only fixes don't bump main version
                if not commit.is_proto_only:
                    result["bump_type"] = "patch"
                else:
                    result["proto_bump"] = True

        # Proto changes
        if commit.is_proto_related:
            result["proto_changes"].append(commit)
            result["proto_bump"] = True

        # Other changes
        if commit.type in ["chore", "docs", "style", "refactor", "test", "build", "ci"]:
            result["other_changes"].append(commit)

    return result


def generate_changelog(
    analysis: dict, current_version: Version, new_version: Version
) -> str:
    """CHANGELOG 항목 생성

    Args:
        analysis: 커밋 분석 결과
        current_version: 현재 버전
        new_version: 새 버전

    Returns:
        CHANGELOG 마크다운 문자열
    """
    lines = [
        f"## [{new_version}] - {import_datetime()}",
        "",
    ]

    if analysis["breaking_changes"]:
        lines.append("### ⚠️ BREAKING CHANGES")
        lines.append("")
        for commit in analysis["breaking_changes"]:
            lines.append(f"- {commit.message} ({commit.sha[:7]})")
        lines.append("")

    if analysis["features"]:
        lines.append("### ✨ Features")
        lines.append("")
        for commit in analysis["features"]:
            lines.append(f"- {commit.message} ({commit.sha[:7]})")
        lines.append("")

    if analysis["fixes"]:
        lines.append("### 🐛 Bug Fixes")
        lines.append("")
        for commit in analysis["fixes"]:
            lines.append(f"- {commit.message} ({commit.sha[:7]})")
        lines.append("")

    if analysis["proto_changes"]:
        lines.append("### 📦 Proto Changes")
        lines.append("")
        for commit in analysis["proto_changes"]:
            if commit not in analysis["features"] + analysis["fixes"]:
                lines.append(f"- {commit.message} ({commit.sha[:7]})")
        lines.append("")

    if analysis["other_changes"]:
        lines.append("### 🔧 Other Changes")
        lines.append("")
        for commit in analysis["other_changes"]:
            lines.append(f"- {commit.message} ({commit.sha[:7]})")
        lines.append("")

    return "\n".join(lines)


def import_datetime() -> str:
    """현재 날짜 반환 (YYYY-MM-DD)"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d")


def auto_bump(
    dry_run: bool = False,
    push: bool = False,
    no_commit: bool = False,
    no_tag: bool = False,
) -> int:
    """Conventional Commits 기반 자동 버전 업데이트

    Args:
        dry_run: 실제 변경 없이 분석만 수행
        push: 변경사항을 origin에 푸시
        no_commit: Git 커밋 생성하지 않음
        no_tag: Git 태그 생성하지 않음

    Returns:
        종료 코드 (0: 성공, 1: 실패)
    """
    try:
        pyproject_path = find_pyproject()
    except FileNotFoundError as e:
        print_error(str(e))
        return 1

    current_version = read_current_version(pyproject_path)

    # Get commits since last tag
    try:
        commits = get_commits_since_tag()
    except subprocess.CalledProcessError as e:
        print_error(f"커밋 목록 가져오기 실패: {e.stderr}")
        return 1

    if not commits:
        print_info("새로운 커밋이 없습니다.")
        return 0

    # Analyze commits
    analysis = analyze_commits(commits)

    # Display analysis
    console.print(f"\n[bold]현재 버전:[/bold] [cyan]{current_version}[/cyan]")
    console.print(f"[bold]분석된 커밋 수:[/bold] {len(commits)}\n")

    if analysis["breaking_changes"]:
        console.print(
            f"[red]⚠️  Breaking Changes: {len(analysis['breaking_changes'])}개[/red]"
        )
    if analysis["features"]:
        console.print(f"[green]✨ Features: {len(analysis['features'])}개[/green]")
    if analysis["fixes"]:
        console.print(f"[yellow]🐛 Bug Fixes: {len(analysis['fixes'])}개[/yellow]")
    if analysis["proto_changes"]:
        console.print(
            f"[blue]📦 Proto Changes: {len(analysis['proto_changes'])}개[/blue]"
        )

    # Determine new version
    if analysis["bump_type"] == "none":
        if analysis["proto_bump"]:
            print_info("\nProto 변경만 있습니다. 메인 버전은 유지됩니다.")
            console.print("[dim]Note: Proto 버전은 별도 관리됩니다 (buf.yaml)[/dim]")
        else:
            print_info("\n버전 변경이 필요한 커밋이 없습니다.")
        return 0

    new_version = current_version.bump(analysis["bump_type"])
    console.print(
        f"\n[yellow]권장 버전:[/yellow] {current_version} → [green]{new_version}[/green] "
        f"([bold]{analysis['bump_type']}[/bold])\n"
    )

    if dry_run:
        print_info("Dry-run 모드: 실제 변경하지 않습니다.")
        # Show what would be in changelog
        changelog = generate_changelog(analysis, current_version, new_version)
        console.print("\n[bold]생성될 CHANGELOG:[/bold]")
        console.print(changelog)
        return 0

    # Write new version
    write_version(pyproject_path, new_version)
    print_success(f"{pyproject_path.name} 업데이트 완료")

    # Git operations
    if not no_commit:
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"], check=True, capture_output=True
            )

            # Add pyproject.toml
            subprocess.run(["git", "add", str(pyproject_path)], check=True)

            # Create commit with conventional format
            commit_msg = f"chore(release): bump version to {new_version}\n\n"
            commit_msg += generate_changelog(analysis, current_version, new_version)

            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print_success(f"커밋 생성 완료: v{new_version}")

            # Create tag
            if not no_tag:
                subprocess.run(["git", "tag", f"v{new_version}"], check=True)
                print_success(f"태그 생성 완료: v{new_version}")

            # Push
            if push:
                subprocess.run(["git", "push", "origin", "HEAD"], check=True)
                print_success("커밋 푸시 완료")
                if not no_tag:
                    subprocess.run(
                        ["git", "push", "origin", f"v{new_version}"], check=True
                    )
                    print_success("태그 푸시 완료")

        except subprocess.CalledProcessError as e:
            print_error(f"Git 작업 실패: {e}")
            return 1

    return 0
