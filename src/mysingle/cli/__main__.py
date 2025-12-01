"""
MySingle CLI - Unified command-line tool.

Currently provides proto management tools.
Future expansion: package management, service scaffolding, etc.
"""

from __future__ import annotations

import sys


def main() -> int:
    """Main entry point for mysingle-cli."""
    print("MySingle CLI v2.0.0")
    print()
    print("Available commands:")
    print("  mysingle-proto    - Proto file management tool")
    print()
    print("Usage:")
    print("  mysingle-proto --help")
    return 0


if __name__ == "__main__":
    sys.exit(main())
