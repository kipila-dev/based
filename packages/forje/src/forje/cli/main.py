# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import platform
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from resforge.io import atomic_write
from rich import box
from rich.table import Table

from forje import __version__
from forje.cli.ui import console, error, success
from forje.cli.utils import format_elapsed
from forje.core.driver import run_pipeline
from forje.core.environment import Environment
from forje.core.errors import ForjeError
from forje.core.loader import load_plugins
from forje.pas.color_norm import ColorCanonicalizer
from forje.pas.resolution import AnnotationsResolver
from forje.pas.validation import PlatformSupport, TargetFilter, TargetValidation

if TYPE_CHECKING:
    from forje.core.pas import Pass

app = typer.Typer(
    name="forje",
    no_args_is_help=True,
    add_completion=False,
)


def _find_build_file() -> Path | None:
    candidate = Path.cwd() / "build.forje"
    return candidate if candidate.exists() else None


def _version_callback(*, value: bool) -> None:
    if value:
        console.print(f"forje {__version__}")
        raise typer.Exit


@app.callback()
def main(
    _: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """Build design system resources from Starlark definitions."""


@app.command()
def build(
    targets: Annotated[
        list[str] | None,
        typer.Option("--target", help="Target to build."),
    ] = None,
) -> None:
    """Build design system resources."""
    build_file = _find_build_file()

    if build_file is None:
        error("build.forje not found in current directory.")
        raise typer.Exit(code=1)

    try:
        source = build_file.read_text(encoding="utf-8")
    except OSError as e:
        error(f"Could not read build.forje: {e.strerror}")
        raise typer.Exit(code=1) from e

    start = time.perf_counter()

    try:
        env = Environment(*load_plugins())

        pipeline: list[Pass] = [
            TargetFilter(targets),
            TargetValidation(),
            PlatformSupport(env),
            AnnotationsResolver(env),
            ColorCanonicalizer(),
            *env.passes,
        ]

        result = run_pipeline(env, source, pipeline)

        for _, _, file_path, file_bytes in result.walk():
            with atomic_write(file_path) as f:
                _ = f.write(file_bytes)
    except* ForjeError as eg:
        for e in eg.exceptions:
            notes = " ".join(getattr(e, "__notes__", []))
            error(f"{e} {notes}".strip())
        raise typer.Exit(code=1) from eg

    elapsed = time.perf_counter() - start
    success(f"Build succeeded in {format_elapsed(elapsed)}")


@app.command()
def doctor() -> None:
    """Diagnose the environment and installed plugins."""
    try:
        env = Environment(*load_plugins())
    except ForjeError as e:
        error(f"Failed to load plugins: {e}")
        raise typer.Exit(code=1) from e

    table = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    table.add_column(style="dim")
    table.add_column(style="bold")
    table.add_row("Python", sys.version.split()[0])
    table.add_row("Platform", platform.platform())
    table.add_row("Forje", __version__)
    table.add_row()
    table.add_row("DSL modules", ",".join(m.name for m in env.modules if m.name))
    table.add_row("Backends", ",".join(env.backends))
    table.add_row("Passes", ",".join(type(p).__name__ for p in env.passes))
    table.add_row("Adapters", ",".join(env.adapters.keys()))
    console.print(table)

    build_file = _find_build_file()
    if build_file:
        success(f"build.forje found at {build_file}")
    else:
        error("build.forje not found in current directory")


if __name__ == "__main__":
    app()
