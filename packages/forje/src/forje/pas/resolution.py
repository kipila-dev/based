# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import contextlib
import dataclasses
from collections.abc import (
    Callable,
    ItemsView,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from collections.abc import Set as AbstractSet
from typing import cast, final, override

from pydantic import TypeAdapter, ValidationError

from forje.core.environment import Environment
from forje.core.errors import ForjeError
from forje.core.pas import Pass
from forje.ir import IR

__all__ = ["AnnotationsResolver"]


def _maybe_resolve_dict(obj: object, adapters: Sequence[TypeAdapter[object]]) -> object:
    if not isinstance(obj, MutableMapping):
        return obj

    obj = cast("MutableMapping[object, object]", obj)

    matches: list[object] = []
    for adapter in adapters:
        with contextlib.suppress(ValidationError):
            matches.append(adapter.validate_python(obj))

    if not matches:
        return obj

    if len(matches) > 1:
        names = ", ".join(type(m).__name__ for m in matches)
        msg = f"Annotations entry matches multiple registered adapters: {names}"
        raise ForjeError(msg)

    return matches[0]


def _resolve(
    obj: object,
    adapters: Sequence[TypeAdapter[object]],
    seen: set[int],
) -> object:
    if id(obj) in seen:
        return obj
    seen.add(id(obj))

    obj = _maybe_resolve_dict(obj, adapters)

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        for field in dataclasses.fields(obj):
            value = cast("object", getattr(obj, field.name))
            resolved = _resolve(value, adapters, seen)
            setattr(obj, field.name, resolved)
        return obj

    if isinstance(obj, MutableMapping):
        for key, value in cast("ItemsView[object, object]", obj.items()):
            obj[key] = _resolve(value, adapters, seen)
        return cast("MutableMapping[object, object]", obj)

    if isinstance(obj, MutableSequence) and not isinstance(obj, (str, bytes)):
        for i, value in enumerate(cast("MutableSequence[object]", obj)):
            obj[i] = _resolve(value, adapters, seen)
        return cast("MutableSequence[object]", obj)

    if isinstance(obj, tuple):
        return tuple(_resolve(v, adapters, seen) for v in cast("tuple[object]", obj))

    if isinstance(obj, AbstractSet) and not isinstance(obj, (str, bytes)):
        return cast("Callable[[object], object]", type(obj))(
            _resolve(v, adapters, seen) for v in obj
        )

    return obj


@final
class AnnotationsResolver(Pass):
    """Resolves raw dicts in `annotations` entries into typed objects."""

    def __init__(self, env: Environment) -> None:
        self._env = env

    @override
    def run(self, ir: IR) -> None:
        _resolve(ir, self._env.annotations_adapters, seen=set())
