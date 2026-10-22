# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from based.core.dsl import Module

__all__ = ["module"]

module = Module(name="dimen", priority=-1000).export_starlark(
    package=__name__,
    resource_name="dimen.star",
)
