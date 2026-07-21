# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, final

from forje.core.frontend import evaluate

if TYPE_CHECKING:
    from forje.core.environment import Environment
    from forje.core.pas import Pass

__all__ = ["Driver"]


@final
class Driver:
    """Orchestrates the compilation and artifact generation pipeline."""

    def __init__(self, env: Environment) -> None:
        self._env = env

    def build(
        self,
        source: str,
        pipeline: list[Pass],
    ) -> dict[str, dict[str, dict[str, bytes]]]:
        """Evaluates the build script and runs the pass pipeline.

        Args:
            source: Contents of a build.forje file.
            pipeline: Ordered list of passes to execute.

        Returns:
            Nested dict keyed by target id -> platform -> file path -> bytes.
        """
        ir = evaluate(self._env, source)

        for pas in pipeline:
            pas.run(ir)

        return ir.outputs
