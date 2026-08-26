# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from forje.ir import BuildGraph

__all__ = ["Pass"]


class Pass(ABC):
    """A compiler pass."""

    """Passes are executed sequentially based on their priority."""
    priority: int = 0

    def __ror__(self, graph: BuildGraph, /) -> BuildGraph:
        return self.run(graph)

    @abstractmethod
    def run(self, graph: BuildGraph) -> BuildGraph:
        """Executes the pass.

        Returns a modified copy of the build graph.
        """
