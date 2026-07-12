import dataclasses
from collections.abc import Mapping, Sequence
from collections.abc import Set as AbstractSet
from typing import cast, final, override

import coloraide

from forje.core.pass_ import Pass
from forje.ir import IR
from forje.ir.models import ColorNode

__all__ = ["ColorCanonicalizer"]


def _normalize_color_node(node: ColorNode) -> None:
    if node.space == "xyz-d65":
        return

    match node.space:
        case "oklch" | "srgb":
            space = node.space
        case "p3":
            space = "display-p3"

    color = coloraide.Color(space, node.coords, alpha=node.alpha).convert("xyz-d65")
    coords = color.coords()
    node.coords = (coords[0], coords[1], coords[2])
    node.alpha = color.alpha()
    node.space = "xyz-d65"


def _walk_and_normalize(obj: object, seen: set[int]) -> None:
    if id(obj) in seen:
        return
    seen.add(id(obj))

    if isinstance(obj, ColorNode):
        _normalize_color_node(obj)
        return

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        for f in dataclasses.fields(obj):
            _walk_and_normalize(cast("object", getattr(obj, f.name)), seen)
    elif isinstance(obj, Mapping):
        for v in obj.values():
            _walk_and_normalize(v, seen)
    elif isinstance(obj, (Sequence, AbstractSet)) and not isinstance(obj, (str, bytes)):
        for v in obj:
            _walk_and_normalize(v, seen)


@final
class ColorCanonicalizer(Pass):
    """Normalizes all `ColorNode` instances in the IR into xyz-d65 color space."""

    @override
    def run(self, ir: IR) -> None:
        _walk_and_normalize(ir, seen=set())
