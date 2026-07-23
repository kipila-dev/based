# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import final

from pydantic import TypeAdapter

from forje.core.backend import Backend
from forje.core.dsl import Module
from forje.core.pas import Pass

__all__ = ["Environment"]


@final
@dataclass(frozen=True)
class Environment:
    """Global configuration for a Forje build.

    It is intended to be initialized once by the build system and passed into
    the `Driver` and `Pass` objects.
    """

    modules: list[Module]
    annotations_adapters: list[TypeAdapter[object]]
    passes: list[Pass]
    backends: dict[str, Backend]
