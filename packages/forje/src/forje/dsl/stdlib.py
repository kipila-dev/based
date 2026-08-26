# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import dataclasses

from forje.core.context import context
from forje.core.dsl import Module
from forje.core.errors import ForjeValidationError
from forje.ir import TargetNode, artifact_adapter, token_adapter

__all__ = ["module"]

module = (
    Module(name="stdlib", priority=-999)
    .export_starlark(
        package=__name__,
        resource_name="token.star",
    )
    .export_starlark(
        package=__name__,
        resource_name="stdlib.star",
    )
)


@module.export(name="_sys_create_target")
def create_target(target_id: str) -> None:
    new_target = TargetNode(id=target_id)
    if target_id in context.graph.targets:
        msg = f"Duplicate target: {target_id}"
        raise ForjeValidationError(msg)
    updated_targets = {**context.graph.targets, target_id: new_target}
    context.graph = dataclasses.replace(context.graph, targets=updated_targets)


@module.export(name="_sys_target_add_token")
def target_add_token(target_id: str, token: dict[str, object]) -> None:
    new_token = token_adapter.validate_python(token)
    try:
        target = context.graph.targets[target_id]
    except LookupError:
        msg = f"Invalid target: {target_id}"
        raise ForjeValidationError(msg) from None
    updated_tokens = {**target.tokens, new_token.name: new_token}
    updated_target = dataclasses.replace(target, tokens=updated_tokens)
    updated_targets = {**context.graph.targets, target_id: updated_target}
    context.graph = dataclasses.replace(context.graph, targets=updated_targets)


@module.export(name="_sys_target_add_artifact")
def target_add_artifact(target_id: str, artifact: dict[str, object]) -> None:
    new_artifact = artifact_adapter.validate_python(artifact)
    try:
        target = context.graph.targets[target_id]
    except LookupError:
        msg = f"Invalid target: {target_id}"
        raise ForjeValidationError(msg) from None
    updated_artifacts = (*target.artifacts, new_artifact)
    updated_target = dataclasses.replace(target, artifacts=updated_artifacts)
    updated_targets = {**context.graph.targets, target_id: updated_target}
    context.graph = dataclasses.replace(context.graph, targets=updated_targets)
