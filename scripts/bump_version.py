#!/usr/bin/env python3
"""
Interactive version bump script for mysingle package.

Features:
- Reads current version from pyproject.toml
- Prompts for bump type: patch / minor / major / custom / abort
- Optionally switches to main branch, pulls latest, applies version bump
- Commits change with "chore(release): vX.Y.Z (bump <type>)"
- Optionally creates a Git tag vX.Y.Z and pushes commit and tag

Requirements: Python 3.12+ (uses tomllib)

Usage:
  python scripts/bump_version.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass

PYPROJECT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "pyproject.toml"
)


@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:  # noqa: D401
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse(cls, s: str) -> "Version":
        m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", s.strip())
        if not m:
            raise ValueError(f"Invalid version: {s}")
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    def bump(self, kind: str) -> "Version":
        if kind == "major":
            return Version(self.major + 1, 0, 0)
        if kind == "minor":
            return Version(self.major, self.minor + 1, 0)
        if kind == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError(f"Unknown bump kind: {kind}")


def run(
    cmd: list[str], check: bool = True, capture_output: bool = False, text: bool = True
) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=capture_output, text=text)


def get_current_branch() -> str:
    res = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
    return res.stdout.strip()


def ensure_clean_worktree() -> None:
    res = run(["git", "status", "--porcelain"], capture_output=True)
    if res.stdout.strip():
        print(
            "\nError: Working tree is not clean. Commit or stash changes before bumping version."
        )
        sys.exit(1)


def read_current_version() -> Version:
    import tomllib  # Python 3.11+

    with open(PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)

    try:
        v = data["project"]["version"]
        return Version.parse(v)
    except KeyError:
        # Fallback: try to find a version line in raw text or initialize
        with open(PYPROJECT_PATH, "r", encoding="utf-8") as fr:
            raw = fr.read()
        m = re.search(r"(?m)^\s*version\s*=\s*\"([^\"]+)\"\s*$", raw)
        if m:
            return Version.parse(m.group(1))
        # No version present; initialize to 0.0.0 as base
        print(
            "\nWarning: No [project].version found in pyproject.toml; initializing from 0.0.0"
        )
        return Version(0, 0, 0)


def write_version(new_version: Version) -> None:
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace existing version line if present
    pattern = re.compile(r'(?m)^(\s*version\s*=\s*")([^\"]+)(\")\s*$')
    if pattern.search(content):
        # Use a function replacement to avoid backreference ambiguity like \11
        content = pattern.sub(
            lambda m: f"{m.group(1)}{new_version}{m.group(3)}", content
        )
    else:
        # Insert after name line if exists within [project] section
        lines = content.splitlines(keepends=True)
        inserted = False
        in_project = False
        new_lines: list[str] = []
        for _i, line in enumerate(lines):
            if line.strip().startswith("[project]"):
                in_project = True
                new_lines.append(line)
                continue
            if in_project and re.match(r"^\s*\[.*\]", line):
                # reached next section without finding name; insert before leaving section
                if not inserted:
                    new_lines.append(f'version = "{new_version}"\n')
                    inserted = True
                new_lines.append(line)
                in_project = False
                continue
            new_lines.append(line)
            if (
                in_project
                and (re.match(r'^\s*name\s*=\s*".*"\s*$', line))
                and not inserted
            ):
                new_lines.append(f'version = "{new_version}"\n')
                inserted = True
        if not inserted:
            # If still not inserted, try to place right after [project] header
            content = re.sub(
                r"(?m)^\[project\]\s*\n",
                f'[project]\nversion = "{new_version}"\n',
                content,
                count=1,
            )
        else:
            content = "".join(new_lines)

    # Also remove any accidental stray backreference artifacts like \11.2.3\3 lines
    content = re.sub(r"(?m)^\\\d+\.[^\n]*\\\d+\s*$", "", content)

    with open(PYPROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def prompt_bump_choice() -> str:
    print("\nSelect version bump type:")
    print("  1) patch")
    print("  2) minor")
    print("  3) major")
    print("  4) custom")
    print("  5) abort")
    while True:
        choice = input("Enter choice [1-5]: ").strip()
        mapping = {
            "1": "patch",
            "2": "minor",
            "3": "major",
            "4": "custom",
            "5": "abort",
        }
        if choice in mapping:
            return mapping[choice]
        print("Invalid choice. Try again.")


def checkout_main_and_pull() -> None:
    run(["git", "checkout", "main"])
    run(["git", "pull", "--ff-only", "origin", "main"])  # fail if diverged


def commit_and_tag(version: Version, bump_kind: str, create_tag: bool) -> None:
    msg = f"chore(release): v{version} (bump {bump_kind})"
    run(["git", "add", PYPROJECT_PATH])
    run(["git", "commit", "-m", msg])
    if create_tag:
        run(["git", "tag", f"v{version}"])


def push_changes(push_tags: bool) -> None:
    run(["git", "push", "origin", "main"])
    if push_tags:
        run(["git", "push", "origin", "--tags"])


def main() -> None:
    print("mysingle: interactive version bump")
    ensure_clean_worktree()

    current_branch = get_current_branch()
    if current_branch != "main":
        ans = (
            input(
                f"\nYou are on branch '{current_branch}'. Switch to 'main' and continue? [Y/n]: "
            )
            .strip()
            .lower()
            or "y"
        )
        if ans.startswith("y"):
            checkout_main_and_pull()
        else:
            print("Aborted.")
            sys.exit(1)

    cur = read_current_version()
    print(f"\nCurrent version: {cur}")

    choice = prompt_bump_choice()
    if choice == "abort":
        print("Aborted.")
        sys.exit(0)

    if choice == "custom":
        while True:
            raw = input("Enter custom version (e.g., 1.4.0): ").strip()
            try:
                new = Version.parse(raw)
                break
            except Exception as e:
                print(f"Invalid version: {e}")
        bump_kind = "custom"
    else:
        new = cur.bump(choice)
        bump_kind = choice

    print(f"\nBumping version: {cur} -> {new} ({bump_kind})")
    confirm = input("Proceed? [Y/n]: ").strip().lower() or "y"
    if not confirm.startswith("y"):
        print("Aborted.")
        sys.exit(0)

    write_version(new)

    tag_ans = input("Create git tag? [Y/n]: ").strip().lower() or "y"
    push_ans = input("Push commit to origin main? [Y/n]: ").strip().lower() or "y"
    push_tag_ans = input("Push tags? [Y/n]: ").strip().lower() or "y"

    commit_and_tag(new, bump_kind, create_tag=tag_ans.startswith("y"))

    if push_ans.startswith("y"):
        push_changes(push_tags=push_tag_ans.startswith("y"))
        print("\nPushed to origin main.")
        if push_tag_ans.startswith("y"):
            print("Pushed tags.")
    else:
        print("\nChanges committed locally. Remember to push when ready.")

    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\nCommand failed: {' '.join(e.cmd)}\n{e.stderr}")
        sys.exit(e.returncode)
