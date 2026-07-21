# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from pydantic import ConfigDict, TypeAdapter
from pydantic.dataclasses import dataclass

from forje.ir import ColorToken

__all__ = ["AgainstNode", "Level", "Role", "against_adapter"]

Role = Literal["text", "large_text", "non_text"]
Level = Literal["aa", "aaa"]


@dataclass(config=ConfigDict(extra="forbid"))
class AgainstNode:
    """A WCAG contrast requirement that links foreground token to a background token."""

    token: ColorToken
    role: Role = "text"
    level: Level = "aa"


against_adapter = TypeAdapter(AgainstNode)
