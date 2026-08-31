# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from typing import Protocol, runtime_checkable

from based.ir import ArtifactNode, TargetNode

__all__ = ["Backend"]


@runtime_checkable
class Backend(Protocol):
    """A platform-specific code generator."""

    def codegen(
        self,
        target: TargetNode,
        artifact: ArtifactNode,
    ) -> dict[str, bytes]:
        """Generates platform assets for a target.

        Returns:
            A dictionary with relative file paths as keys and file content as values.
        """
        ...
