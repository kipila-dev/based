# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import math
from pathlib import Path
from typing import final, override

from based.core.backend import Backend
from based.core.io import MemorySink
from based.ir import (
    ArtifactNode,
    Color,
    ColorNode,
    ColorSelector,
    DimensionKind,
    DimensionNode,
    TargetNode,
)
from based.ir.utils import get_config

__all__ = ["CSS"]

_SUPPORTS_OKLCH = "@supports (color: oklch(0% 0 0))"
_PREFERS_CONTRAST = "(prefers-contrast: more)"
_PREFERS_LIGHT = "(prefers-color-scheme: light)"
_PREFERS_DARK = "(prefers-color-scheme: dark)"
_MEDIA_COLOR_SCHEME_QUERIES: dict[ColorSelector, str] = {
    "light": "",
    "dark": f"@media {_PREFERS_DARK}",
    "high_contrast_light": f"@media {_PREFERS_CONTRAST} and {_PREFERS_LIGHT}",
    "high_contrast_dark": f"@media {_PREFERS_CONTRAST} and {_PREFERS_DARK}",
}
_ATTR_COLOR_SCHEME_SELECTORS: dict[ColorSelector, str] = {
    "light": ':root[data-theme="light"]',
    "dark": ':root[data-theme="dark"]',
    "high_contrast_dark": ':root[data-theme="high-contrast-dark"]',
    "high_contrast_light": ':root[data-theme="high-contrast-light"]',
}
_UNITS: dict[DimensionKind, str] = {
    "spacing": "rem",
    "font": "rem",
    "size": "px",
}


def _fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _to_var(typ: str, name: str, value: str) -> str:
    name = name.replace(".", "-")
    return f"--{typ}-{name}: {value};"


def _alpha_suffix(alpha: float) -> str:
    return "" if alpha == 1 else f" / {_fmt(alpha)}"


def _color_to_vars(name: str, node: ColorNode) -> tuple[str, str]:
    color = Color(
        x=node.coords[0],
        y=node.coords[1],
        z=node.coords[2],
        alpha=node.alpha,
    )

    r, g, b, a_srgb = color.to_srgb_components()
    r, g, b = (round(c * 255) for c in (r, g, b))

    l, c, h, a_oklch = color.to_oklch_components()
    h = "none" if math.isnan(h) else _fmt(h)

    rgb = f"rgb({r} {g} {b}{_alpha_suffix(a_srgb)})"
    oklch = f"oklch({_fmt(l)} {_fmt(c)} {h}{_alpha_suffix(a_oklch)})"

    return _to_var("color", name, rgb), _to_var("color", name, oklch)


def _dimen_to_var(name: str, node: DimensionNode) -> str:
    return _to_var("dimen", name, f"{node.value}{_UNITS[node.kind]}")


def _indent(text: str | list[str], level: int = 1) -> str:
    if isinstance(text, str):
        text = text.split("\n")
    prefix = "  " * level
    return "\n".join(f"{prefix}{line}" if line else "" for line in text)


def _block(selector: str, body: str | list[str]) -> str:
    if not body:
        return ""
    return f"{selector} {{\n{_indent(body)}\n}}"


def _wrap(body: str, *wrappers: str) -> str:
    for wrapper in reversed([w for w in wrappers if w]):
        body = _block(wrapper, body)
    return body


def _render_media_color_scheme(selector_to_vars: dict[ColorSelector, list[str]]) -> str:
    blocks = [
        _wrap(_block(":root", v), _MEDIA_COLOR_SCHEME_QUERIES[s])
        for s, v in selector_to_vars.items()
        if v
    ]
    return "\n\n".join(blocks)


def _render_attr_color_scheme(selector_to_vars: dict[ColorSelector, list[str]]) -> str:
    blocks = [
        _block(_ATTR_COLOR_SCHEME_SELECTORS[s], v)
        for s, v in selector_to_vars.items()
        if v
    ]
    return "\n\n".join(blocks)


def _render_color_scheme(selector_to_vars: dict[ColorSelector, list[str]]) -> str:
    return "\n\n".join(
        b
        for b in (
            _render_media_color_scheme(selector_to_vars),
            _render_attr_color_scheme(selector_to_vars),
        )
        if b
    )


def _empty_color_scheme_vars() -> dict[ColorSelector, list[str]]:
    return {s: [] for s in _MEDIA_COLOR_SCHEME_QUERIES}


@final
class CSS(Backend):
    """Generates CSS custom properties from design tokens."""

    @override
    def codegen(self, target: TargetNode, artifact: ArtifactNode) -> dict[str, bytes]:
        rgb = _empty_color_scheme_vars()
        oklch = _empty_color_scheme_vars()
        dimensions: list[str] = []

        for token in target.tokens.values():
            if token.kind == "color":
                for selector, node in token.variants.items():
                    rgb_var, oklch_var = _color_to_vars(token.name, node)
                    rgb[selector].append(rgb_var)
                    oklch[selector].append(oklch_var)
            elif token.kind == "dimension":
                dimensions.append(_dimen_to_var(token.name, token.variants["default"]))

        sections = [
            _block(":root", dimensions),
            _render_color_scheme(rgb),
        ]

        if oklch_body := _render_color_scheme(oklch):
            sections.append(_wrap(oklch_body, _SUPPORTS_OKLCH))

        css = "\n\n".join(s for s in sections if s) + "\n"

        stem = get_config(artifact.config, "stem", "tokens")
        sink = MemorySink()
        sink.write(Path(artifact.path) / f"{stem}.css", css.encode())
        return sink.files
