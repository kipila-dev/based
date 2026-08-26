# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.resources
from types import FunctionType
from typing import TYPE_CHECKING, Self, final

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Module"]


@final
class Module:
    """Manages exporting of Python definitions and Starlark sources to the DSL."""

    def __init__(self, name: str | None, *, priority: int = 0) -> None:
        """Initialize a new module.

        Args:
            name: Starlark module name. If omitted, the exported definitions
                will be injected into the default Starlark module.
            priority: Module load priority. Lower values are loaded earlier.
        """
        self.name = name
        self.priority = priority
        self.python: dict[str, Callable[..., object] | object] = {}
        self.starlark: list[str] = []

    def export[F: FunctionType](
        self,
        *,
        name: str | None = None,
    ) -> Callable[[F], F]:
        """Decorates a function to be exported.

        Args:
            name: An optional custom name for the exported function.
                If omitted, the function's own name is used.
        """

        def decorator(fun: F) -> F:
            export_name = (name or "").strip() or fun.__name__
            self.python[export_name] = fun
            return fun

        return decorator

    def export_value(self, name: str, value: object) -> Self:
        """Exports a static value."""
        self.python[name] = value
        return self

    def export_starlark(self, package: str, resource_name: str) -> Self:
        """Exports Starlark definitions."""
        self.starlark.append(
            importlib.resources.files(package)
            .joinpath(resource_name)
            .read_text("utf-8"),
        )
        return self
