# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

# Initialize the development environment
setup:
    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg
