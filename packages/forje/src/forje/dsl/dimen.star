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
    return DimensionRecord(value=value, kind=kind)


dimen = struct(
    DimensionRecord=DimensionRecord,
    DimensionSelector=DimensionSelector,
    Dimension=Dimension,
)
