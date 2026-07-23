# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import re
from typing import final, override

from resforge import Color
from resforge.apple import Appearance, AppleColor, AssetCatalog
from resforge.io import MemorySink

from forje.core.backend import Backend
from forje.ir import ArtifactNode, ColorNode, ColorSelector, TargetNode
from forje.ir.utils import get_config

_APPEARANCE_MAP: dict[ColorSelector, list[Appearance]] = {
    "light": [],
    "dark": [Appearance.Dark],
    "high_contrast_light": [Appearance.HighContrast, Appearance.Light],
    "high_contrast_dark": [Appearance.HighContrast, Appearance.Dark],
}


def _to_pascal_case(value: str) -> str:
    words = re.split(r"[-_]+", value)
    return "".join(w.capitalize() for w in words if w)


def _to_color(node: ColorNode) -> Color:
    return Color(x=node.coords[0], y=node.coords[1], z=node.coords[2], alpha=node.alpha)


@final
class Apple(Backend):
    """Generates Apple Asset Catalogs from design tokens."""

    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        color_tokens = (t for t in target.tokens.values() if t.kind == "color")
        sink = MemorySink()

        with AssetCatalog(
            artifact.path,
            get_config(artifact.config, "stem", "Assets"),
            sink=sink,
        ) as catalog:
            for token in color_tokens:
                name = _to_pascal_case(token.name)
                apple_colors = [
                    AppleColor(_to_color(node), appearances=_APPEARANCE_MAP[mode])
                    for mode, node in token.variants.items()
                ]
                catalog.colorset(name, *apple_colors)

        return sink.files
