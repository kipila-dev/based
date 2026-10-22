# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import starlark

from based.core.context import context_scope
from based.core.errors import BasedEvalError, BasedParseError

if TYPE_CHECKING:
    from collections.abc import Callable

    from based.core.dsl import Module
    from based.core.environment import Environment
    from based.ir import BuildGraph

__all__ = ["BUILD_FILE_NAME", "evaluate"]

BUILD_FILE_NAME = "build.based"

_DIALECT = starlark.Dialect.extended()
_DIALECT.enable_f_strings = True

_GLOBALS = starlark.Globals.standard().extended_by(
    [
        starlark.LibraryExtension.EnumType,
        starlark.LibraryExtension.Filter,
        starlark.LibraryExtension.Json,
        starlark.LibraryExtension.Map,
        starlark.LibraryExtension.Partial,
        starlark.LibraryExtension.Pprint,
        starlark.LibraryExtension.Print,
        starlark.LibraryExtension.RecordType,
        starlark.LibraryExtension.RustDecimal,
        starlark.LibraryExtension.StructType,
        starlark.LibraryExtension.Typing,
    ],
)


def _build_module(
    module: Module,
    loader: Callable[..., starlark.FrozenModule],
    into: starlark.Module | None = None,
) -> starlark.Module | starlark.FrozenModule:
    mod = starlark.Module() if into is None else into

    for name, value in module.python.items():
        if callable(value):
            mod.add_callable(name, value)
        else:
            mod[name] = value

    for script in module.starlark:
        _parse_and_eval(
            (module.name or "").strip() or BUILD_FILE_NAME,
            script,
            mod,
            loader,
        )

    return mod.freeze() if into is None else mod


def _build_dsl(
    env: Environment,
) -> tuple[starlark.Module, Callable[..., starlark.FrozenModule]]:

    modules: dict[str, starlark.FrozenModule] = {}
    default_module = starlark.Module()

    def loader(name: str) -> starlark.FrozenModule:
        if name in modules:
            return modules[name]
        raise FileNotFoundError

    for module in env.modules:
        if module.name is None:
            _ = _build_module(module, loader, into=default_module)
        else:
            mod = _build_module(module, loader)
            if isinstance(mod, starlark.FrozenModule):
                modules[module.name] = mod

    return default_module, loader


def _parse_and_eval(
    name: str,
    source: str,
    module: starlark.Module,
    loader: Callable[..., starlark.FrozenModule],
) -> None:
    try:
        ast = starlark.parse(name, source, dialect=_DIALECT)
    except starlark.StarlarkError as e:
        raise BasedParseError(str(e)) from e

    try:
        _ = starlark.eval(module, ast, _GLOBALS, starlark.FileLoader(loader))
    except starlark.StarlarkError as e:
        raise BasedEvalError(str(e)) from e


def evaluate(env: Environment, source: str) -> BuildGraph:
    """Evaluate a build script.

    Args:
        env: The build environment instance.
        source: The build script contents as a string.

    Raises:
        BasedParseError: If the source contains a Starlark syntax error.
        BasedEvalError: If the source fails during Starlark evaluation.
    """
    with context_scope() as ctx:
        module, loader = _build_dsl(env)
        _parse_and_eval(BUILD_FILE_NAME, source, module, loader)
        return ctx.graph
