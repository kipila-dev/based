# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, final

from forje.ir import BuildGraph

if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = ["BuildContext", "context", "context_scope"]

_ctx: ContextVar[BuildContext] = ContextVar("ctx")


class BuildContext(Protocol):
    """Build state for a single Forje evaluation."""

    graph: BuildGraph


@final
@dataclass
class _Context:
    graph: BuildGraph


@final
class _ContextProxy(BuildContext):
    @property
    def graph(self) -> BuildGraph:
        return _ctx.get().graph

    @graph.setter
    def graph(self, value: BuildGraph) -> None:
        _ctx.get().graph = value


context: BuildContext = _ContextProxy()


@contextmanager
def context_scope(graph: BuildGraph | None = None) -> Iterator[BuildContext]:
    """Yields a new build context."""
    graph = graph or BuildGraph()
    token = _ctx.set(_Context(graph))
    try:
        yield context
    finally:
        _ctx.reset(token)
