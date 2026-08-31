# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

from pygls.lsp.server import LanguageServer

from based_lsp import __version__

_server = LanguageServer("based-lsp", f"v{__version__}")


def main() -> None:
    """Starts the language server."""
    _server.start_io()
