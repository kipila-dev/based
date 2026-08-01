# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import dataclasses
from typing import cast, final, override

import coloraide

from forje.core.pas import Pass
from forje.ir import IR
from forje.ir.models import ColorNode
from forje.ir.utils import walk_ir

__all__ = ["ColorCanonicalizer"]


def _normalize_color_node(node: object) -> object:
    if not isinstance(node, ColorNode) or node.space == "xyz-d65":
        return node

    color = coloraide.Color(node.space, node.coords, alpha=node.alpha).convert(
        "xyz-d65",
    )

    coords = color.coords()

    changes = {
        "coords": (coords[0], coords[1], coords[2]),
        "alpha": color.alpha(),
        "space": "xyz-d65",
    }

    return dataclasses.replace(node, **changes)


@final
class ColorCanonicalizer(Pass):
    """Normalizes all `ColorNode` instances in the IR into xyz-d65 color space."""

    @override
    def run(self, ir: IR) -> IR:
        return cast("IR", walk_ir(ir, _normalize_color_node))
