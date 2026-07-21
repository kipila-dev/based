# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

_ColorSpace = enum("oklch", "display-p3", "srgb", "xyz-d65")
ColorSpace = struct(
    OKLCH=_ColorSpace("oklch"),
    DISPLAY_P3=_ColorSpace("display-p3"),
    SRGB=_ColorSpace("srgb"),
    XYZ_D65=_ColorSpace("xyz-d65"),
)

ColorRecord = record(coords=list[int | float], alpha=float, space=_ColorSpace)

ColorSelector = enum("light", "dark", "high_contrast_light", "high_contrast_dark")


def Color(
    *value,
    alpha: float | None = None,
    space: _ColorSpace = ColorSpace.SRGB,
) -> ColorRecord:
    """Creates a color definition.

    Args:
        *value: Either a hex string (e.g., "#FF0000") or three floats
            representing color coordinates (e.g., 1.0, 0.0, 0.0).
        alpha: Optional alpha channel value (0.0 to 1.0). If provided,
            it overrides any alpha parsed from a hex string.
        space: The color space for float inputs. Defaults to sRGB.
    """
    if isinstance(value[0], str):
        r, g, b, a = _sys_color_parse_hex(value[0])
        return ColorRecord(
            coords=[r, g, b],
            alpha=alpha if alpha != None else a,
            space=ColorSpace.SRGB,
        )

    if (
        len(value) == 3
        and isinstance(value[0], int | float)
        and isinstance(value[1], int | float)
        and isinstance(value[2], int | float)
    ):
        return ColorRecord(
            coords=[value[0], value[1], value[2]],
            alpha=alpha if alpha != None else 1.0,
            space=space,
        )

    fail("Invalid value: '{}'.".format(value))


def _oklch(
    l: int | float,
    c: int | float,
    h: int | float,
    alpha: float = 1.0,
) -> ColorRecord:
    if not (0 <= l and l <= 1):
        fail("OKLCh lightness must be in [0.0, 1.0]")
    if c < 0:
        fail("OKLCh chroma must be non-negative")
    if not (0 <= alpha and alpha <= 1):
        fail("Alpha must be in [0.0, 1.0]")
    return ColorRecord(coords=[l, c, h], alpha=alpha, space=ColorSpace.OKLCH)


def _display_p3(
    r: int | float,
    g: int | float,
    b: int | float,
    alpha: float = 1.0,
) -> ColorRecord:
    if not (0 <= r and r <= 1 and 0 <= g and g <= 1 and 0 <= b and b <= 1):
        fail("Display P3 components must be in [0.0, 1.0]")
    if not (0 <= alpha and alpha <= 1):
        fail("Alpha must be in [0.0, 1.0]")
    return ColorRecord(coords=[r, g, b], alpha=alpha, space=ColorSpace.DISPLAY_P3)


def _srgb(
    r: int | float,
    g: int | float,
    b: int | float,
    alpha: float = 1.0,
) -> ColorRecord:
    if not (0 <= r and r <= 1 and 0 <= g and g <= 1 and 0 <= b and b <= 1):
        fail("sRGB components must be in [0.0, 1.0]")
    if not (0 <= alpha and alpha <= 1):
        fail("Alpha must be in [0.0, 1.0]")
    return ColorRecord(coords=[r, g, b], alpha=alpha, space=ColorSpace.SRGB)


def _xyz_d65(
    x: int | float,
    y: int | float,
    z: int | float,
    alpha: float = 1.0,
) -> ColorRecord:
    if not (0 <= alpha and alpha <= 1):
        fail("Alpha must be in [0.0, 1.0]")
    return ColorRecord(coords=[x, y, z], alpha=alpha, space=ColorSpace.XYZ_D65)


color = struct(
    ColorSpace=ColorSpace,
    ColorRecord=ColorRecord,
    ColorSelector=ColorSelector,
    Color=Color,
    oklch=_oklch,
    display_p3=_display_p3,
    srgb=_srgb,
    xyz_d65=_xyz_d65,
)
