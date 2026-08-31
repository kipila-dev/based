# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, Protocol, runtime_checkable

__all__ = ["require_context"]


@runtime_checkable
class _HasActiveContext(Protocol):
    _active: bool


def require_context[T: _HasActiveContext, **P, R](
    fun: Callable[Concatenate[T, P], R],
) -> Callable[Concatenate[T, P], R]:
    """Ensures a method is only called within an active context.

    Raises:
        RuntimeError: If the method is called while the instance's
            `_active` attribute is False.

    """

    @wraps(fun)
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        if not self._active:
            fun_name = getattr(fun, "__name__", "unknown")
            msg = f"'{fun_name}' requires an active 'with' context."
            raise RuntimeError(msg)
        return fun(self, *args, **kwargs)

    return wrapper
