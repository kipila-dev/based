# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import contextlib
from collections.abc import Mapping
from typing import cast, final, override

from pydantic import ValidationError

from forje.core.environment import Environment
from forje.core.pas import Pass
from forje.ir import IR
from forje.ir.utils import walk_ir

__all__ = ["DictResolver"]


@final
class DictResolver(Pass):
    """Resolves raw dicts with registered TypeAdapters into typed objects."""

    def __init__(self, env: Environment) -> None:
        self._env = env

    @override
    def run(self, ir: IR) -> IR:
        return cast("IR", walk_ir(ir, self._maybe_resolve_dict))

    def _maybe_resolve_dict(self, obj: object) -> object:
        if not isinstance(obj, Mapping):
            return obj

        obj = cast("Mapping[object, object]", obj)

        matches: list[object] = []
        for adapter in self._env.adapters.values():
            with contextlib.suppress(ValidationError):
                matches.append(adapter.validate_python(obj))

        if not matches:
            return obj

        if len(matches) > 1:
            names = ", ".join(type(m).__name__ for m in matches)
            msg = f"Entry matches multiple registered adapters: {names}"
            raise ValueError(msg)

        return matches[0]
