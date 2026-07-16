load("stdlib", "TokenRecord")

_Role = enum("text", "large_text", "non_text")
_Level = enum("aa", "aaa")

Role = struct(
    Text=_Role("text"),
    LargeText=_Role("large_text"),
    NonText=_Role("non_text"),
)

Level = struct(
    AA=_Level("aa"),
    AAA=_Level("aaa"),
)

AgainstRecord = record(token=TokenRecord, role=_Role, level=_Level)


def against(
    token: TokenRecord,
    *,
    role: _Role = Role.Text,
    level: _Level = Level.AA,
) -> AgainstRecord:
    token = TokenRecord(
        name=token.name,
        kind=token.kind,
        variants=token.variants,
        annotations=[],
    )
    return AgainstRecord(token=token, role=role, level=level)


wcag = struct(
    against=against,
    Role=Role,
    Level=Level,
)
