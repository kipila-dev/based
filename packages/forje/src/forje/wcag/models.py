from typing import Literal

from pydantic import ConfigDict, TypeAdapter
from pydantic.dataclasses import dataclass

from forje.ir import TokenNode

__all__ = ["AgainstNode", "Level", "Role", "against_adapter"]

Role = Literal["text", "large_text", "non_text"]
Level = Literal["aa", "aaa"]


@dataclass(config=ConfigDict(extra="forbid"))
class AgainstNode:
    """A WCAG contrast requirement that links foreground token to a background token."""

    token: TokenNode
    role: Role = "text"
    level: Level = "aa"


against_adapter = TypeAdapter(AgainstNode)
