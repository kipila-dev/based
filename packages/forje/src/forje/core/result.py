# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import final

from forje.core.environment import Environment
from forje.ir import BuildGraph

__all__ = ["CompilationResult", "codegen"]


@final
@dataclass
class CompilationResult:
    """Compilation result."""

    outputs: dict[str, dict[str, dict[str, bytes]]] = field(default_factory=dict)

    def __bool__(self) -> bool:
        """Returns True if at least one file exists across all targets and platforms."""
        return any(
            files for platforms in self.outputs.values() for files in platforms.values()
        )

    def __len__(self) -> int:
        """Returns the total number of files across all targets and platforms."""
        return sum(
            len(files)
            for platforms in self.outputs.values()
            for files in platforms.values()
        )

    def walk(self) -> Iterator[tuple[str, str, str, bytes]]:
        """Yields (target, platform, file_path, file_bytes) for every compiled file."""
        for target, platforms in self.outputs.items():
            for platform, files in platforms.items():
                for file_path, file_bytes in files.items():
                    yield target, platform, file_path, file_bytes


def codegen(env: Environment, graph: BuildGraph) -> CompilationResult:
    """Runs code generation for all targets in the given build graph."""
    result = CompilationResult()
    for target in graph.targets.values():
        result.outputs[target.id] = {}
        for artifact in target.artifacts:
            files = env.backends[artifact.platform].codegen(target, artifact)
            result.outputs[target.id][artifact.platform] = files
    return result
