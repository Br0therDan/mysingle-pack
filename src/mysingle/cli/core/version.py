"""Version management command."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


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
    """Find pyproject.toml in current directory or parents."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            return pyproject
    raise FileNotFoundError("pyproject.toml not found")


def read_current_version(pyproject_path: Path) -> Version:
    """Read version from pyproject.toml."""
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
    """Get current version from pyproject.toml.

    Returns:
        Version: Current version

    Raises:
        FileNotFoundError: If pyproject.toml not found
    """
    pyproject_path = find_pyproject()
    return read_current_version(pyproject_path)


def write_version(pyproject_path: Path, new_version: Version) -> None:
    """Write new version to pyproject.toml."""
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
    """Run git command."""
    return subprocess.run(["git"] + args, check=check, capture_output=True, text=True)


def setup_parser(parser: argparse.ArgumentParser) -> None:
    """Setup version command parser."""
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch", "show"],
        help="Version bump type or 'show' to display current version",
    )
    parser.add_argument(
        "--custom",
        help="Custom version string (e.g., 2.1.0)",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Don't create git commit",
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="Don't create git tag",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push commit and tag to origin",
    )


def execute(args: argparse.Namespace) -> int:
    """Execute version command."""
    try:
        pyproject_path = find_pyproject()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1

    current = read_current_version(pyproject_path)

    if args.bump_type == "show":
        print(f"Current version: {current}")
        return 0

    # Determine new version
    if args.custom:
        try:
            new_version = Version.parse(args.custom)
        except ValueError as e:
            print(f"❌ {e}")
            return 1
    else:
        new_version = current.bump(args.bump_type)

    print(f"Bumping version: {current} -> {new_version}")

    # Write new version
    write_version(pyproject_path, new_version)
    print(f"✅ Updated {pyproject_path.name}")

    # Git operations
    if not args.no_commit:
        try:
            # Check if git repo
            run_git(["rev-parse", "--git-dir"])

            # Add and commit
            run_git(["add", str(pyproject_path)])
            msg = f"chore(release): v{new_version} (bump {args.bump_type})"
            run_git(["commit", "-m", msg])
            print(f"✅ Committed: {msg}")

            # Create tag
            if not args.no_tag:
                run_git(["tag", f"v{new_version}"])
                print(f"✅ Tagged: v{new_version}")

            # Push
            if args.push:
                run_git(["push", "origin", "HEAD"])
                print("✅ Pushed commit")
                if not args.no_tag:
                    run_git(["push", "origin", f"v{new_version}"])
                    print("✅ Pushed tag")

        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git operation failed: {e.stderr}")
            return 1

    return 0
