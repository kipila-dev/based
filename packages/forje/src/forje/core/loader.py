# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import importlib.metadata
from typing import TYPE_CHECKING, cast

from pydantic import TypeAdapter

from forje.core.backend import Backend
from forje.core.dsl import Module
from forje.core.errors import ForjePluginLoadError
from forje.core.pas import Pass

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["load_plugins"]


def _load[T](
    group: str,
    expected_type: type[T],
    *,
    instantiate: bool = False,
) -> list[tuple[str, T]]:
    results: list[tuple[str, T]] = []

    for ep in importlib.metadata.entry_points(group=group):
        try:
            loaded = cast("object", ep.load())
            if instantiate:
                loaded = cast("Callable[[], object]", loaded)()
        except Exception as e:
            msg = f"Failed to resolve entry point '{ep.name}': {e}"
            raise ForjePluginLoadError(msg) from e

        if not isinstance(loaded, expected_type):
            msg = (
                f"Invalid entry point '{ep.name}': "
                f"must resolve to a {expected_type.__name__} instance"
            )
            raise ForjePluginLoadError(msg)

        results.append((ep.name, loaded))

    return results


def load_plugins() -> tuple[
    list[Module],
    list[TypeAdapter[object]],
    list[Pass],
    dict[str, Backend],
]:
    """Discovers and loads all registered plugins.

    Raises:
        ForjePluginLoadError: If a plugin fails to resolve, fails to
            instantiate, or does not match the expected type.
    """
    modules = [m for _, m in _load("forje.dsl", Module)]
    modules.sort(key=lambda m: m.priority)

    adapters: list[tuple[str, TypeAdapter[object]]] = _load(
        "forje.annotations_adapter",
        TypeAdapter,
    )
    annotations_adapters = [a for _, a in adapters]

    passes = [p for _, p in _load("forje.pass", Pass, instantiate=True)]
    passes.sort(key=lambda p: p.priority)

    backends = dict(_load("forje.backend", Backend, instantiate=True))

    return modules, annotations_adapters, passes, backends
