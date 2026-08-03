# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Annotated, Literal, cast

from pydantic import BeforeValidator, ConfigDict, Field, TypeAdapter
from pydantic.dataclasses import dataclass

__all__ = [
    "IR",
    "ArtifactNode",
    "ColorNode",
    "ColorSpace",
    "ColorToken",
    "DimensionNode",
    "DimensionToken",
    "ImmutableMapping",
    "TargetNode",
    "TokenNode",
    "artifact_adapter",
    "color_adapter",
    "dimen_adapter",
    "target_adapter",
    "token_adapter",
]


def _to_mapping_proxy[K, V](value: Mapping[K, V]) -> MappingProxyType[K, V]:
    if isinstance(value, MappingProxyType):
        return cast("MappingProxyType[K, V]", value)
    return MappingProxyType(dict(value))


type ImmutableMapping[K, V] = Annotated[
    Mapping[K, V],
    BeforeValidator(_to_mapping_proxy),
]


ColorSpace = Literal["oklch", "display-p3", "srgb", "xyz-d65"]
ColorSelector = Literal["light", "dark", "high_contrast_light", "high_contrast_dark"]
type ColorToken = TokenNode[ColorNode, Literal["color"], ColorSelector]

DimensionKind = Literal["spacing", "size", "font"]
DimensionSelector = Literal["default"]
type DimensionToken = TokenNode[DimensionNode, Literal["dimension"], DimensionSelector]


TokenKind = Literal["color", "dimension"]
type AnySelector = ColorSelector | DimensionSelector
type AnyToken = Annotated[ColorToken | DimensionToken, Field(discriminator="kind")]


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class ValueNode:
    """Base class for token values."""


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class ColorNode(ValueNode):
    """A color value in a specific color space."""

    coords: tuple[float, float, float]
    alpha: float = 1.0
    space: ColorSpace = "srgb"
    type: Literal["color"] = "color"


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class DimensionNode(ValueNode):
    """A dimension value."""

    value: int | float
    kind: DimensionKind
    type: Literal["dimension"] = "dimension"


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class TokenNode[T: ValueNode, K: TokenKind, S: AnySelector]:
    """A named design token with one or more variants."""

    name: str
    kind: K
    variants: ImmutableMapping[S, T]
    annotations: tuple[object, ...] = Field(default_factory=tuple)


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class ArtifactNode:
    """Output configuration for a single platform."""

    platform: str
    path: str
    config: ImmutableMapping[str, object] = Field(default_factory=dict)


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class TargetNode:
    """A named build target grouping tokens and artifact configs."""

    id: str
    tokens: ImmutableMapping[str, AnyToken] = Field(default_factory=dict)
    artifacts: tuple[ArtifactNode, ...] = Field(default_factory=tuple)


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class IR:
    """The intermediate representation of a parsed build script."""

    targets: ImmutableMapping[str, TargetNode] = Field(default_factory=dict)


artifact_adapter = TypeAdapter(ArtifactNode)
color_adapter = TypeAdapter(ColorNode)
dimen_adapter = TypeAdapter(DimensionNode)
target_adapter = TypeAdapter(TargetNode)
token_adapter: TypeAdapter[AnyToken] = TypeAdapter(AnyToken)
