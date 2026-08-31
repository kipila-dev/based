# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

_DimensionKind = enum("spacing", "size", "font")
DimensionKind = struct(
    Spacing=_DimensionKind("spacing"),
    Size=_DimensionKind("size"),
    Font=_DimensionKind("font"),
)
DimensionRecord = record(value=int | float, kind=_DimensionKind)
DimensionSelector = enum("default")


def Dimension(
    value: int | float,
    kind: _DimensionKind = DimensionKind.Size,
) -> DimensionRecord:
    """Creates a dimension definition.

    Args:
        value: The numeric value.
        kind: The semantic kind (spacing, size, font). Defaults to Size.
    """
    return DimensionRecord(value=value, kind=kind)


def _spacing(value: int | float) -> DimensionRecord:
    return DimensionRecord(value=value, kind=DimensionKind.Spacing)


def _size(value: int | float) -> DimensionRecord:
    return DimensionRecord(value=value, kind=DimensionKind.Size)


def _font(value: int | float) -> DimensionRecord:
    return DimensionRecord(value=value, kind=DimensionKind.Font)


dimen = struct(
    DimensionRecord=DimensionRecord,
    DimensionSelector=DimensionSelector,
    Dimension=Dimension,
    Spacing=_spacing,
    Size=_size,
    Font=_font,
)
