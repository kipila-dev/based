# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import final, override

from resforge import Color
from resforge.android import ComposeWriter
from resforge.io import MemorySink

from based.core.backend import Backend
from based.core.errors import BasedError
from based.ir import ArtifactNode, ColorNode, ColorSelector, TargetNode
from based.ir.utils import get_config


def _to_resforge_color(node: ColorNode) -> Color:
    return Color(x=node.coords[0], y=node.coords[1], z=node.coords[2], alpha=node.alpha)


def _to_resforge_colors(nodes: dict[str, ColorNode]) -> dict[str, Color]:
    return {k: _to_resforge_color(v) for k, v in nodes.items()}


@final
class Compose(Backend):
    """Generates Jetpack Compose Kotlin files for colors from design tokens."""

    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        package = get_config(artifact.config, "package", "")
        if not package:
            msg = "Compose backend requires 'package' argument"
            raise BasedError(msg)

        sink = MemorySink()
        color_tokens = [t for t in target.tokens.values() if t.kind == "color"]

        if not color_tokens:
            return sink.files

        def get_variant(selector: ColorSelector) -> dict[str, ColorNode]:
            return {
                t.name: t.variants[selector]
                for t in color_tokens
                if selector in t.variants
            }

        light_colors = _to_resforge_colors(get_variant("light"))
        dark_colors = _to_resforge_colors(get_variant("dark"))

        stem = get_config(artifact.config, "stem", "Theme")
        path = Path(artifact.path) / f"{stem}.kt"

        with ComposeWriter(path, package=package, sink=sink) as compose:
            if light_colors:
                with compose.object_("LightColors") as light:
                    light.color(**light_colors)
            if dark_colors:
                with compose.object_("DarkColors") as dark:
                    dark.color(**dark_colors)

        return sink.files
