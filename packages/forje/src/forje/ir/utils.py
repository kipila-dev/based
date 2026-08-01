# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import dataclasses
from collections.abc import Callable, Mapping, Sequence
from collections.abc import Set as AbstractSet
from typing import TYPE_CHECKING, cast

from forje.ir.models import ImmutableMapping

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

__all__ = ["get_config", "walk_ir"]


def walk_ir(
    obj: object,
    visitor: Callable[[object], object],
    *,
    seen: set[int] | None = None,
) -> object:
    """Walks the IR graph recursively and applies `visitor` to each value.

    Returns:
        A transformed copy of the IR graph.
    """
    if seen is None:
        seen = set()

    if _is_traversable(obj):
        obj_id = id(obj)
        if obj_id in seen:
            return obj
        seen.add(obj_id)

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return _walk_dataclass(obj, visitor, seen)

    if isinstance(obj, Mapping):
        return _walk_mapping(cast("Mapping[object, object]", obj), visitor, seen)

    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        return _walk_sequence(obj, visitor, seen)

    if isinstance(obj, AbstractSet) and not isinstance(obj, (str, bytes)):
        return _walk_set(obj, visitor, seen)

    return visitor(obj)


def get_config[T](
    config: ImmutableMapping[str, object],
    key: str,
    default: T,
    *,
    strip: bool = True,
) -> T:
    """Retrieves a value from a configuration dictionary with type validation."""
    value = config.get(key)
    if value is None:
        return default

    expected_type = type(default)

    if expected_type is bool:
        if not isinstance(value, bool):
            raise _type_error(key, expected_type, value)
    elif expected_type is int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise _type_error(key, expected_type, value)
    elif not isinstance(value, expected_type):
        raise _type_error(key, expected_type, value)

    if isinstance(value, str) and strip:
        value = value.strip()
        if not value:
            return default

    return cast("T", value)


def _type_error(key: str, expected_type: type, value: object) -> ValueError:
    msg = (
        f"Invalid value for '{key}': "
        f"required '{expected_type.__name__}', got '{type(value).__name__}'"
    )
    return ValueError(msg)


def _is_traversable(obj: object) -> bool:
    return (dataclasses.is_dataclass(obj) and not isinstance(obj, type)) or (
        isinstance(obj, (Mapping, Sequence, AbstractSet))
        and not isinstance(obj, (str, bytes))
    )


def _walk_dataclass(
    obj: "DataclassInstance",
    visitor: Callable[[object], object],
    seen: set[int],
) -> object:
    changes = {
        f.name: walk_ir(cast("object", getattr(obj, f.name)), visitor, seen=seen)
        for f in dataclasses.fields(obj)
        if f.init
    }
    return visitor(dataclasses.replace(obj, **changes))


def _walk_mapping(
    obj: Mapping[object, object],
    visitor: Callable[[object], object],
    seen: set[int],
) -> object:
    items = [(k, walk_ir(v, visitor, seen=seen)) for k, v in obj.items()]
    constructor = cast("Callable[[object], object]", type(obj))
    try:
        result = constructor(items)
    except TypeError:
        result = dict(items)
    return visitor(result)


def _walk_sequence(
    obj: Sequence[object],
    visitor: Callable[[object], object],
    seen: set[int],
) -> object:
    values = tuple(walk_ir(v, visitor, seen=seen) for v in obj)
    constructor = cast("Callable[[object], object]", type(obj))
    try:
        result = constructor(values)
    except TypeError:
        result = values
    return visitor(result)


def _walk_set(
    obj: AbstractSet[object],
    visitor: Callable[[object], object],
    seen: set[int],
) -> object:
    try:
        values = {walk_ir(v, visitor, seen=seen) for v in obj}
    except TypeError:
        values = [walk_ir(v, visitor, seen=seen) for v in obj]
    constructor = cast("Callable[[object], object]", type(obj))
    try:
        result = constructor(values)
    except TypeError:
        result = values
    return visitor(result)
