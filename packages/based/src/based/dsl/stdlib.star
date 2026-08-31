# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

ArtifactRecord = record(
    platform=str,
    path=str,
    config=field(dict[str, typing.Any] | None, default=None),
)


def Artifact(platform: str, path: str, **config: dict) -> ArtifactRecord:
    return ArtifactRecord(platform=platform, path=path, config=config)


def target(
    *,
    id: str,
    tokens: list[TokenRecord],
    artifacts: list[ArtifactRecord],
) -> None:
    _internal_create_target(id)
    for token in tokens:
        _internal_target_add_token(id, token)
    for artifact in artifacts:
        _internal_target_add_artifact(id, artifact)
