# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.resources
from functools import partial
from types import FunctionType
from typing import TYPE_CHECKING, Self, final, get_type_hints

from forje.core.context import Context, context_proxy

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Module"]


@final
class Module:
    """Manages exporting of Python definitions and Starlark sources to the DSL."""

    def __init__(self, name: str | None, *, priority: int = 0) -> None:
        """Initialize a new DSL module.

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
        """Decorates a function to be exported to the DSL.

        If the function signature contains a 'ctx' parameter, it is automatically
        partially applied with the context proxy.

        Args:
            name: An optional custom name for the exported function.
                If omitted, the function's own name is used.
        """

        def decorator(fun: F) -> F:
            export_name = (name or "").strip() or fun.__name__

            target = fun
            hints = get_type_hints(fun)
            for param, annotation in hints.items():
                if annotation is Context:
                    target = partial(fun, **{param: context_proxy})
                    break

            self.python[export_name] = target
            return fun

        return decorator

    def export_value(self, name: str, value: object) -> Self:
        """Exports a static value to the DSL."""
        self.python[name] = value
        return self

    def export_starlark(self, package: str, resource_name: str) -> Self:
        """Exports Starlark definitions to the DSL."""
        self.starlark.append(
            importlib.resources.files(package)
            .joinpath(resource_name)
            .read_text("utf-8"),
        )
        return self
