# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import time
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from resforge.io import atomic_write
from rich import print  # noqa: A004

from forje import __version__
from forje.cli.ui import error, success
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
        print(f"forje {__version__}")
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


if __name__ == "__main__":
    app()
