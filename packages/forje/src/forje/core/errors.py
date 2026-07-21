# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

__all__ = [
    "ForjeError",
    "ForjeEvalError",
    "ForjeParseError",
    "ForjePluginLoadError",
    "ForjeValidationError",
]


class ForjeError(Exception):
    """Base class for all Forje errors."""


class ForjePluginLoadError(ForjeError):
    """Error while loading external plugin."""


class ForjeParseError(ForjeError):
    """Starlark parse error in build.forje."""


class ForjeEvalError(ForjeError):
    """Starlark evaluation error in build.forje."""


class ForjeValidationError(ForjeError):
    """Domain constraint violation."""
