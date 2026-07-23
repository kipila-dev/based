# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

from forje.core.frontend import evaluate
from forje.core.result import CompilationResult, codegen

if TYPE_CHECKING:
    from forje.core.environment import Environment
    from forje.core.pas import Pass

__all__ = ["run_pipeline"]


def run_pipeline(
    env: Environment,
    source: str,
    pipeline: list[Pass],
) -> CompilationResult:
    """Evaluates the build script, runs the pass pipeline, and emits artifacts.

    Args:
        env: The build environment.
        source: Contents of the build script file.
        pipeline: Ordered list of passes to execute.
    """
    ir = evaluate(env, source)

    for pas in pipeline:
        pas.run(ir)

    return codegen(env, ir)
