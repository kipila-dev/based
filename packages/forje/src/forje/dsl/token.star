load("color", "ColorRecord", "ColorSelector")
load("dimen", "DimensionRecord", "DimensionSelector")

_AnySelector = [ColorSelector, DimensionSelector]
_AnyValue = [ColorRecord, DimensionRecord]

_TokenKind = enum("color", "dimension")
TokenKind = struct(
    Color=_TokenKind("color"),
    Dimension=_TokenKind("dimension"),
)

TokenRecord = record(
    name=str,
    kind=_TokenKind,
    variants=dict[_AnySelector, _AnyValue],
    annotations=list[typing.Any],
)


def ColorToken(
    name: str,
    variants=dict[ColorSelector, ColorRecord],
    annotations=list[typing.Any],
) -> TokenRecord:
    return TokenRecord(
        name=name,
        kind=TokenKind.Color,
        variants=variants,
        annotations=annotations,
    )


def DimensionToken(
    name: str,
    variants=dict[DimensionSelector, DimensionRecord],
    annotations=list[typing.Any],
) -> TokenRecord:
    return TokenRecord(
        name=name,
        kind=TokenKind.Dimension,
        variants=variants,
        annotations=annotations,
    )


def Token(
    name: str,
    value: _AnyValue | None = None,
    annotations: typing.Any | list[typing.Any] | None = None,
    **variants: dict[str, _AnyValue],
) -> TokenRecord:
    if isinstance(annotations, list[typing.Any]):
        annotations = annotations
    elif annotations == None:
        annotations = []
    else:
        annotations = [annotations]

    if isinstance(value, ColorRecord):
        return ColorToken(
            name=name,
            variants={ColorSelector("light"): value},
            annotations=annotations,
        )

    if isinstance(value, DimensionRecord):
        return DimensionToken(
            name=name,
            variants={DimensionSelector("default"): value},
            annotations=annotations,
        )

    if variants:
        if isinstance(variants.values()[0], ColorRecord):
            return ColorToken(
                name=name,
                variants={ColorSelector(k): v for k, v in variants.items()},
                annotations=annotations,
            )

        if isinstance(variants.values()[0], DimensionRecord):
            return DimensionToken(
                name=name,
                variants={DimensionSelector(k): v for k, v in variants.items()},
                annotations=annotations,
            )

    fail("Token must have a value")
