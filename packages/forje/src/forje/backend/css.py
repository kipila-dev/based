import math
from pathlib import Path
from typing import final, override

from resforge import Color
from resforge.io import MemorySink

from forje.backend import Backend
from forje.ir import ArtifactNode, ColorNode, ColorSelector, TargetNode
from forje.ir.utils import get_config

__all__ = ["CSS"]

_SUPPORTS_OKLCH = "@supports (color: oklch(0% 0 0))"
_QUERY_CONTRAST = "(prefers-contrast: more)"
_QUERY_LIGHT = "(prefers-color-scheme: light)"
_QUERY_DARK = "(prefers-color-scheme: dark)"
_QUERIES: dict[ColorSelector, str] = {
    "light": "",
    "dark": f"@media {_QUERY_DARK}",
    "high_contrast_light": f"@media {_QUERY_CONTRAST} and {_QUERY_LIGHT}",
    "high_contrast_dark": f"@media {_QUERY_CONTRAST} and {_QUERY_DARK}",
}


def _to_color(node: ColorNode) -> Color:
    return Color(x=node.coords[0], y=node.coords[1], z=node.coords[2], alpha=node.alpha)


def _to_css_vars(name: str, node: ColorNode) -> tuple[str, str]:
    name = f"--color-{name.lower().strip().replace('_', '-')}"
    color = _to_color(node)

    r, g, b, a_srgb = color.to_srgb_components()
    r, g, b = round(r * 255), round(g * 255), round(b * 255)

    l, c, h, a_oklch = color.to_oklch_components()
    h = "none" if math.isnan(h) else round(h, 3)

    return (
        f"{name}: rgb({r} {g} {b} / {a_srgb:.3f});",
        f"{name}: oklch({l:.3f} {c:.3f} {h} / {a_oklch:.3f});",
    )


def _indent(text: str | list[str], level: int = 1) -> str:
    if isinstance(text, str):
        text = text.split("\n")
    prefix = "  " * level
    return "\n".join(f"{prefix}{line}" if line else "" for line in text)


def _wrap(body: str, *rules: str) -> str:
    for rule in filter(None, rules):
        body = f"{rule} {{\n{_indent(body)}\n}}"
    return body


def _render(selector_to_var: dict[ColorSelector, list[str]]) -> str:
    blocks = [
        _wrap(f":root {{\n{_indent(var)}\n}}", _QUERIES[selector])
        for selector, var in selector_to_var.items()
        if var
    ]
    return "\n\n".join(blocks)


@final
class CSS(Backend):
    """Generates CSS custom properties from design tokens."""

    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        rgb: dict[ColorSelector, list[str]] = {s: [] for s in _QUERIES}
        oklch: dict[ColorSelector, list[str]] = {s: [] for s in _QUERIES}

        color_tokens = [t for t in target.tokens.values() if t.kind == "color"]
        for token in color_tokens:
            for selector, node in token.variants.items():
                rgb_var, oklch_var = _to_css_vars(token.name, node)
                rgb[selector].append(rgb_var)
                oklch[selector].append(oklch_var)

        sections = [_render(rgb)]
        if oklch_section := _render(oklch):
            sections.append(_wrap(oklch_section, _SUPPORTS_OKLCH))

        css = "\n\n".join(sections) + "\n"

        stem = get_config(artifact.config, "stem", "tokens")
        sink = MemorySink()
        sink.write(Path(artifact.path) / f"{stem}.css", css.encode())
        return sink.files
