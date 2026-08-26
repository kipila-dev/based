# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import re
from typing import cast, final, override

from forje.core.environment import Environment
from forje.core.errors import ForjeError
from forje.core.pas import Pass
from forje.ir import BuildGraph, TokenNode
from forje.ir.utils import walk_build_graph

__all__ = ["PlatformSupport", "TargetFilter", "TargetValidation", "TokenNameValidator"]


@final
class TargetFilter(Pass):
    """Restricts the active targets to the specified subset.

    If no targets are provided, all targets are kept.
    """

    def __init__(self, active_targets: list[str] | None = None) -> None:
        self._active_targets = active_targets or []

    @override
    def run(self, graph: BuildGraph) -> BuildGraph:
        if not self._active_targets:
            return graph

        all_targets = [t.id for t in graph.targets.values()]
        unknown_targets = [t for t in self._active_targets if t not in all_targets]
        if unknown_targets:
            noun = "target" if len(unknown_targets) == 1 else "targets"
            msg = f"Unknown {noun}: {', '.join(unknown_targets)}"
            raise ForjeError(msg)

        targets = {k: v for k, v in graph.targets.items() if k in self._active_targets}
        return dataclasses.replace(graph, targets=targets)


@final
class TargetValidation(Pass):
    """Validates target configuration constraints."""

    @override
    def run(self, graph: BuildGraph) -> BuildGraph:
        if not graph.targets:
            msg = "No targets defined in the build configuration"
            raise ForjeError(msg)

        empty_targets = [t.id for t in graph.targets.values() if not t.tokens]
        if empty_targets:
            noun = "target" if len(empty_targets) == 1 else "targets"
            msg = f"Empty {noun}: {', '.join(empty_targets)}"
            raise ForjeError(msg)

        return graph


@final
class PlatformSupport(Pass):
    """Verifies that every artifact platform has a registered backend."""

    def __init__(self, env: Environment) -> None:
        self._env = env

    @override
    def run(self, graph: BuildGraph) -> BuildGraph:
        all_platforms = self._env.backends.keys()
        active_platforms = {
            a.platform for t in graph.targets.values() for a in t.artifacts
        }
        unknown_platforms = active_platforms - all_platforms

        if unknown_platforms:
            platforms = ", ".join(f"'{p}'" for p in sorted(unknown_platforms))
            msg = f"No backend registered for platforms: {platforms}"
            raise ForjeError(msg)

        return graph


@final
class TokenNameValidator(Pass):
    """Verifies that every token name follows dot notation."""

    _pattern = re.compile(r"^[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*$")

    @override
    def run(self, graph: BuildGraph) -> BuildGraph:
        return cast("BuildGraph", walk_build_graph(graph, self._validate_token_name))

    def _validate_token_name(self, obj: object) -> object:
        if isinstance(obj, TokenNode) and not self._pattern.fullmatch(obj.name):
            msg = f"Invalid token name: '{obj.name}'"
            raise ForjeError(msg)
        return obj
