from dataclasses import dataclass
from typing import final

from pydantic import TypeAdapter

from forje.backend import Backend
from forje.core.pass_ import Pass
from forje.dsl import Module

__all__ = ["Environment"]


@final
@dataclass(frozen=True)
class Environment:
    """Global configuration for a Forje build.

    It is intended to be initialized once by the build system and passed into
    the `Driver` and `Pass` objects.
    """

    modules: list[Module]
    context_adapters: list[TypeAdapter[object]]
    passes: list[Pass]
    backends: dict[str, Backend]
