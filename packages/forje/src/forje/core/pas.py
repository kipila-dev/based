# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from forje.ir import IR

__all__ = ["Pass"]


class Pass(ABC):
    """A compiler pass.

    Passes are executed sequentially by the `Driver` pipeline and are allowed
    to modify the `IR` in-place.
    """

    priority: int = 0

    @abstractmethod
    def run(self, ir: IR) -> None:
        """Executes the compiler pass logic on the given IR instance."""
