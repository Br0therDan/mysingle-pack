"""
MySingle CLI - Unified command-line tool.

Currently provides proto management tools.
Future expansion: package management, service scaffolding, etc.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    """Main entry point for mysingle-cli."""
    parser = argparse.ArgumentParser(
        prog="mysingle-cli",
        description="MySingle Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Version command
    from .core import version as version_cmd

    version_parser = subparsers.add_parser(
        "version",
        help="Manage package version",
        description="Bump package version and create releases",
    )
    version_cmd.setup_parser(version_parser)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if args.command == "version":
        return version_cmd.execute(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
