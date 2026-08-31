# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

__all__ = [
    "BasedError",
    "BasedEvalError",
    "BasedParseError",
    "BasedPluginLoadError",
    "BasedValidationError",
]


class BasedError(Exception):
    """Base class for all errors."""


class BasedPluginLoadError(BasedError):
    """Error while loading external plugin."""


class BasedParseError(BasedError):
    """Starlark parse error in build script."""


class BasedEvalError(BasedError):
    """Starlark evaluation error in build script."""


class BasedValidationError(BasedError):
    """Domain constraint violation."""
