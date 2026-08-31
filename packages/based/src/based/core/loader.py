# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import importlib.metadata
from typing import TYPE_CHECKING, cast

from pydantic import TypeAdapter

from based.core.backend import Backend
from based.core.dsl import Module
from based.core.errors import BasedPluginLoadError
from based.core.pas import Pass

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
            raise BasedPluginLoadError(msg) from e

        if not isinstance(loaded, expected_type):
            msg = (
                f"Invalid entry point '{ep.name}': "
                f"must resolve to a {expected_type.__name__} instance"
            )
            raise BasedPluginLoadError(msg)

        results.append((ep.name, loaded))

    return results


def load_plugins() -> tuple[
    list[Module],
    dict[str, TypeAdapter[object]],
    list[Pass],
    dict[str, Backend],
]:
    """Discovers and loads all registered plugins.

    Raises:
        BasedPluginLoadError: If a plugin fails to resolve, fails to
            instantiate, or does not match the expected type.
    """
    modules = [m for _, m in _load("based.dsl", Module)]
    modules.sort(key=lambda m: m.priority)

    adapters: dict[str, TypeAdapter[object]] = dict(_load("based.adapter", TypeAdapter))

    passes = [p for _, p in _load("based.pass", Pass, instantiate=True)]
    passes.sort(key=lambda p: p.priority)

    backends = dict(_load("based.backend", Backend, instantiate=True))

    return modules, adapters, passes, backends
