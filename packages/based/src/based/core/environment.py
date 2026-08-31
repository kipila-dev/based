# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import final

from pydantic import TypeAdapter

from based.core.backend import Backend
from based.core.dsl import Module
from based.core.pas import Pass

__all__ = ["Environment"]


@final
@dataclass(frozen=True)
class Environment:
    """Global build configuration."""

    modules: list[Module]
    adapters: dict[str, TypeAdapter[object]]
    passes: list[Pass]
    backends: dict[str, Backend]
