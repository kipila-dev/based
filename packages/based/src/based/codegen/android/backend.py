# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import final, override

from based.codegen.android import ValuesWriter
from based.core.backend import Backend
from based.core.io import MemorySink, WriteSink
from based.ir import ArtifactNode, Color, ColorNode, ColorSelector, TargetNode
from based.ir.utils import get_config


def _to_color(node: ColorNode) -> Color:
    return Color(x=node.coords[0], y=node.coords[1], z=node.coords[2], alpha=node.alpha)


def _write_tokens(sink: WriteSink, path: Path, nodes: dict[str, ColorNode]) -> None:
    with ValuesWriter(path, sink=sink) as res:
        colors = {name: _to_color(node) for name, node in nodes.items()}
        res.color(**colors)


@final
class Android(Backend):
    """Generates Android XML resource files for colors from design tokens."""

    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        colors = [t for t in target.tokens.values() if t.kind == "color"]

        def get_variant(selector: ColorSelector) -> dict[str, ColorNode]:
            return {
                t.name: t.variants[selector] for t in colors if selector in t.variants
            }

        light = get_variant("light")
        dark = get_variant("dark")

        sink = MemorySink()
        base_path = Path(artifact.path)
        stem = get_config(artifact.config, "stem", "colors")

        _write_tokens(sink, base_path / "values" / f"{stem}.xml", light)
        _write_tokens(sink, base_path / "values-night" / f"{stem}.xml", dark)

        return sink.files
