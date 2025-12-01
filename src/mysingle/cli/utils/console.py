"""Console utilities with rich formatting."""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

# Global console instance
console = Console()


def print_success(message: str) -> None:
    """Print success message in green."""
    console.print(f"✅ {message}", style="bold green")


def print_error(message: str) -> None:
    """Print error message in red."""
    console.print(f"❌ {message}", style="bold red")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    console.print(f"⚠️  {message}", style="bold yellow")


def print_info(message: str) -> None:
    """Print info message in blue."""
    console.print(f"ℹ️  {message}", style="bold cyan")


def print_header(title: str) -> None:
    """Print section header."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]\n")


def ask_choice(prompt: str, choices: list[str], default: str | None = None) -> str:
    """Ask user to select from choices.

    Args:
        prompt: Question to ask
        choices: List of valid choices
        default: Default choice (optional)

    Returns:
        Selected choice
    """
    choices_str = "/".join(choices)
    if default:
        prompt_text = f"{prompt} [{choices_str}] (기본: {default})"
    else:
        prompt_text = f"{prompt} [{choices_str}]"

    while True:
        answer = Prompt.ask(prompt_text, default=default or "")
        if answer in choices:
            return answer
        print_error(
            f"'{answer}'은(는) 유효하지 않은 선택입니다. {choices_str} 중 하나를 선택하세요."
        )


def ask_confirm(prompt: str, default: bool = False) -> bool:
    """Ask yes/no question.

    Args:
        prompt: Question to ask
        default: Default answer

    Returns:
        True if yes, False if no
    """
    return Confirm.ask(prompt, default=default)


def ask_text(prompt: str, default: str = "") -> str:
    """Ask for text input.

    Args:
        prompt: Question to ask
        default: Default value

    Returns:
        User input
    """
    return Prompt.ask(prompt, default=default)


def create_table(title: str, columns: list[str]) -> Table:
    """Create a formatted table.

    Args:
        title: Table title
        columns: Column names

    Returns:
        Rich Table instance
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for col in columns:
        table.add_column(col)
    return table
