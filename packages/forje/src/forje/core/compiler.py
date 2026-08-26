# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

from forje.core.frontend import evaluate
from forje.core.result import CompilationResult, codegen
from forje.pas.color_norm import ColorCanonicalizer
from forje.pas.resolver import DictResolver
from forje.pas.validation import (
    PlatformSupport,
    TargetFilter,
    TargetValidation,
    TokenNameValidator,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from forje.core.environment import Environment
    from forje.core.pas import Pass

__all__ = ["compile_source", "default_pipeline"]


def default_pipeline(env: Environment, targets: list[str] | None) -> Sequence[Pass]:
    """Builds the default pipeline configuration."""
    return [
        TargetFilter(targets),
        TargetValidation(),
        PlatformSupport(env),
        DictResolver(env),
        TokenNameValidator(),
        ColorCanonicalizer(),
        *env.passes,
    ]


def compile_source(
    source: str,
    env: Environment,
    pipeline: Sequence[Pass],
) -> CompilationResult:
    """Evaluates the build script, runs the pass pipeline, and emits artifacts.

    Args:
        env: The build environment.
        source: Contents of the build script file.
        pipeline: Ordered list of passes to execute.
    """
    graph = evaluate(env, source)

    for pas in pipeline:
        graph = graph | pas

    return codegen(env, graph)
