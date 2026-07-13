from collections.abc import Generator
from typing import final, override

import coloraide

from forje.core.errors import ForjeValidationError
from forje.core.pas import Pass
from forje.ir import IR, ColorNode, TargetNode, TokenMapping, TokenNode
from forje.wcag.models import AgainstNode, Level, Role

__all__ = ["WCAGValidation"]

_WCAG_THRESHOLDS: dict[tuple[Role, Level], float] = {
    ("text", "aa"): 4.5,
    ("text", "aaa"): 7.0,
    ("large_text", "aa"): 3.0,
    ("large_text", "aaa"): 4.5,
    ("non_text", "aa"): 3.0,
    ("non_text", "aaa"): 3.0,
}


def _walk_wcag_tokens(
    ir: IR,
) -> Generator[tuple[TargetNode, TokenNode, list[AgainstNode]]]:
    for target in ir.targets.values():
        for token in target.tokens.values():
            wcag_nodes = [n for n in token.context if isinstance(n, AgainstNode)]
            if wcag_nodes:
                yield target, token, wcag_nodes


def _expand_mapping(
    mapping: dict[TokenMapping, ColorNode],
) -> dict[TokenMapping, ColorNode]:
    light = mapping["light"]
    dark = mapping.get("dark", light)
    return {
        "light": light,
        "dark": dark,
        "high_contrast_light": mapping.get("high_contrast_light", light),
        "high_contrast_dark": mapping.get("high_contrast_dark", dark),
    }


def _make_coloraide_color(node: ColorNode) -> coloraide.Color:
    return coloraide.Color("xyz-d65", node.coords, node.alpha)


def _validate_contrast(
    target: TargetNode,
    token: TokenNode,
    against: AgainstNode,
) -> list[ForjeValidationError]:
    errors: list[ForjeValidationError] = []

    variants = token.mapping.keys() | against.token.mapping.keys()
    token_expanded = _expand_mapping(token.mapping)
    against_expanded = _expand_mapping(against.token.mapping)
    token_mapping = {k: v for k, v in token_expanded.items() if k in variants}
    against_mapping = {k: v for k, v in against_expanded.items() if k in variants}
    required_contrast = _WCAG_THRESHOLDS[(against.role, against.level)]

    for variant in variants:
        token_color = _make_coloraide_color(token_mapping[variant])
        against_color = _make_coloraide_color(against_mapping[variant])
        contrast_ratio = token_color.contrast(against_color, "wcag21")

        if contrast_ratio < required_contrast:
            msg = (
                f"{target.id}: WCAG {against.level.upper()} contrast failure "
                f"({against.role}, {variant}): "
                f"'{token.name}' against '{against.token.name}' "
                f"is {contrast_ratio:.2f}:1, requires ≥ {required_contrast:.1f}:1"
            )
            errors.append(ForjeValidationError(msg))

    return errors


@final
class WCAGValidation(Pass):
    """Validates contrast ratios for tokens with WCAG constraints in `context`."""

    @override
    def run(self, ir: IR) -> None:
        errors: list[ForjeValidationError] = []

        for target, token, wcag_nodes in _walk_wcag_tokens(ir):
            for node in wcag_nodes:
                errors.extend(_validate_contrast(target, token, node))

        if errors:
            msg = "WCAG validation failed"
            raise ExceptionGroup(msg, errors)
