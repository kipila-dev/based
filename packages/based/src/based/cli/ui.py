# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import typer
from rich.console import Console

__all__ = ["console", "error", "success"]

console = Console(soft_wrap=True)


def error(message: str) -> None:
    """Prints a formatted error message."""
    typer.secho(f"Error: {message}", fg=typer.colors.RED, err=True)


def success(message: str) -> None:
    """Prints a formatted success message."""
    typer.secho(message, fg=typer.colors.GREEN)
