# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from based.core.dsl import Module

from .wcag import WCAGValidation

__all__ = ["WCAGValidation", "module"]

module = Module(name="wcag").export_starlark(
    package=__name__,
    resource_name="wcag.star",
)
