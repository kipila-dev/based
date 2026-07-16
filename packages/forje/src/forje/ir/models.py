from __future__ import annotations

from typing import Annotated, Literal

from pydantic import ConfigDict, Field, TypeAdapter
from pydantic.dataclasses import dataclass

__all__ = [
    "IR",
    "ArtifactNode",
    "ColorNode",
    "ColorSpace",
    "ColorToken",
    "DimensionNode",
    "DimensionToken",
    "TargetNode",
    "TokenNode",
    "artifact_adapter",
    "color_adapter",
    "dimen_adapter",
    "target_adapter",
    "token_adapter",
]

ColorSpace = Literal["oklch", "display-p3", "srgb", "xyz-d65"]
DimensionKind = Literal["spacing", "size", "font"]
ColorSelector = Literal["light", "dark", "high_contrast_light", "high_contrast_dark"]
DimensionSelector = Literal["default"]
TokenKind = Literal["color", "dimension"]

type ColorToken = TokenNode[ColorNode, Literal["color"], ColorSelector]
type DimensionToken = TokenNode[DimensionNode, Literal["dimension"], DimensionSelector]
type AnySelector = ColorSelector | DimensionSelector
type AnyToken = Annotated[ColorToken | DimensionToken, Field(discriminator="kind")]


@dataclass(config=ConfigDict(extra="forbid"))
class ValueNode:
    """Base class for token values."""


@dataclass(config=ConfigDict(extra="forbid"))
class ColorNode(ValueNode):
    """A color value in a specific color space."""

    coords: tuple[float, float, float]
    alpha: float = 1.0
    space: ColorSpace = "srgb"
    type: Literal["color"] = "color"


@dataclass(config=ConfigDict(extra="forbid"))
class DimensionNode(ValueNode):
    """A dimension value."""

    value: int | float
    kind: DimensionKind
    type: Literal["dimension"] = "dimension"


@dataclass(config=ConfigDict(extra="forbid"))
class TokenNode[T: ValueNode, K: TokenKind, S: AnySelector]:
    """A named design token with one or more variants."""

    name: str
    kind: K
    variants: dict[S, T]
    context: list[object] = Field(default_factory=list)


@dataclass(config=ConfigDict(extra="forbid"))
class ArtifactNode:
    """Output configuration for a single platform."""

    platform: str
    path: str
    config: dict[str, object] = Field(default_factory=dict)


@dataclass(config=ConfigDict(extra="forbid"))
class TargetNode:
    """A named build target grouping tokens and artifact configs."""

    id: str
    tokens: dict[str, AnyToken] = Field(default_factory=dict)
    artifacts: list[ArtifactNode] = Field(default_factory=list)


@dataclass
class IR:
    """The intermediate representation of a parsed build script."""

    targets: dict[str, TargetNode] = Field(default_factory=dict)
    outputs: dict[str, dict[str, dict[str, bytes]]] = Field(default_factory=dict)


artifact_adapter = TypeAdapter(ArtifactNode)
color_adapter = TypeAdapter(ColorNode)
dimen_adapter = TypeAdapter(DimensionNode)
target_adapter = TypeAdapter(TargetNode)
token_adapter: TypeAdapter[AnyToken] = TypeAdapter(AnyToken)
