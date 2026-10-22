# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import re

from based.core.dsl import Module

__all__ = ["module"]

module = Module(name="color", priority=-1000).export_starlark(
    package=__name__,
    resource_name="color.star",
)

_hex_color_re = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})")


@module.export(name="_internal_color_parse_hex")
def color_parse_hex(value: str) -> tuple[float, float, float, float]:
    if not _hex_color_re.fullmatch(value):
        msg = f"Invalid hex color: {value!r}"
        raise ValueError(msg)

    hex_str = value[1:]

    if len(hex_str) in (3, 4):
        hex_str = "".join(c * 2 for c in hex_str)

    if len(hex_str) == 6:
        hex_str = hex_str + "FF"

    r, g, b, a = bytes.fromhex(hex_str)

    return r / 255, g / 255, b / 255, a / 255
