# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

from based.core.frontend import evaluate
from based.core.result import CompilationResult, codegen
from based.pas.color_norm import ColorCanonicalizer
from based.pas.resolver import DictResolver
from based.pas.validation import (
    PlatformSupport,
    TargetFilter,
    TargetValidation,
    TokenNameValidator,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from based.core.environment import Environment
    from based.core.pas import Pass

__all__ = ["compile_source", "standard_pipeline"]


def standard_pipeline(env: Environment, targets: list[str] | None) -> Sequence[Pass]:
    """Returns the standard pipeline configuration."""
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
    """Evaluates the build script, runs the pass pipeline, and runs code generation.

    Args:
        source: Contents of the build script file.
        env: The build environment.
        pipeline: Ordered list of passes to execute.
    """
    graph = evaluate(env, source)

    for pas in pipeline:
        graph = graph | pas

    return codegen(env, graph)
