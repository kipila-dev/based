# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from forje.core.dsl import Module

__version__ = "1.0.1"
__all__ = ["module"]

module = Module(name="tailwind").export_starlark(
    package=__name__,
    resource_name="tailwind.star",
)
