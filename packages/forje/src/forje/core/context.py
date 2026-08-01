# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from threading import RLock
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from forje.ir import IR

__all__ = ["Context", "context_proxy"]

_ctx: ContextVar[Context] = ContextVar("ctx")


@final
@dataclass
class Context:
    """Mutable build state for a single Forje evaluation."""

    ir: IR
    lock: RLock = field(init=False, default_factory=RLock)


class _ContextProxy:
    @property
    def ir(self) -> IR:
        return _ctx.get().ir

    @ir.setter
    def ir(self, value: IR) -> None:
        _ctx.get().ir = value

    @property
    def lock(self) -> RLock:
        return _ctx.get().lock

    @classmethod
    def set_context(cls, ctx: Context) -> Token[Context]:
        """Sets the current context."""
        return _ctx.set(ctx)

    @classmethod
    def reset_context(cls, token: Token[Context]) -> None:
        """Resets the context to the state before set_context was called."""
        _ctx.reset(token)


context_proxy = _ContextProxy()
