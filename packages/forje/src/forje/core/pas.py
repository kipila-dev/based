# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from forje.ir import IR

__all__ = ["Pass"]


class Pass(ABC):
    """A compiler pass.

    Passes are executed sequentially by the driver based on their priority.
    """

    priority: int = 0

    def __ror__(self, ir: IR, /) -> IR:
        return self.run(ir)

    @abstractmethod
    def run(self, ir: IR) -> IR:
        """Executes the compiler pass and returns a new IR copy."""
