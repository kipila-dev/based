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
    context=list[typing.Any],
)


def ColorToken(
    name: str,
    variants=dict[ColorSelector, ColorRecord],
    context=list[typing.Any],
) -> TokenRecord:
    return TokenRecord(
        name=name,
        kind=TokenKind.Color,
        variants=variants,
        context=context,
    )


def DimensionToken(
    name: str,
    variants=dict[DimensionSelector, DimensionRecord],
    context=list[typing.Any],
) -> TokenRecord:
    return TokenRecord(
        name=name,
        kind=TokenKind.Dimension,
        variants=variants,
        context=context,
    )


def Token(
    name: str,
    value: _AnyValue | None = None,
    context: typing.Any | list[typing.Any] | None = None,
    **variants: dict[str, _AnyValue],
) -> TokenRecord:
    if isinstance(context, list[typing.Any]):
        context = context
    elif context == None:
        context = []
    else:
        context = [context]

    if isinstance(value, ColorRecord):
        return ColorToken(
            name=name,
            variants={ColorSelector("light"): value},
            context=context,
        )

    if isinstance(value, DimensionRecord):
        return DimensionToken(
            name=name,
            variants={DimensionSelector("default"): value},
            context=context,
        )

    if variants:
        if isinstance(variants.values()[0], ColorRecord):
            return ColorToken(
                name=name,
                variants={ColorSelector(k): v for k, v in variants.items()},
                context=context,
            )

        if isinstance(variants.values()[0], DimensionRecord):
            return DimensionToken(
                name=name,
                variants={DimensionSelector(k): v for k, v in variants.items()},
                context=context,
            )

    fail("Token must have a value")
