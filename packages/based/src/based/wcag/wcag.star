# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

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

ContrastRecord = record(token=TokenRecord, role=_Role, level=_Level)


def contrast(
    token: TokenRecord,
    *,
    role: _Role = Role.Text,
    level: _Level = Level.AA,
) -> ContrastRecord:
    return ContrastRecord(
        token=TokenRecord(
            name=token.name,
            kind=token.kind,
            variants=token.variants,
            annotations=[],
        ),
        role=role,
        level=level,
    )


wcag = struct(
    contrast=contrast,
    Role=Role,
    Level=Level,
)
