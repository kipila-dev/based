# SPDX-FileCopyrightText: 2026 Kipila Ltd
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Protocol, override, runtime_checkable

__all__ = ["FileSystemSink", "MemorySink", "WriteSink", "atomic_write"]


@contextmanager
def atomic_write(target_path: str | Path) -> Iterator[IO[bytes]]:
    """Yields a temporary file, then atomically replaces target_path on success.

    Preserves file permissions if `target_path` already exists.
    """
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with NamedTemporaryFile(
            dir=target_path.parent,
            delete=False,
            suffix=".tmp",
        ) as tf:
            temp_path = Path(tf.name)
            yield tf

            tf.flush()
            os.fsync(tf.fileno())

        try:
            shutil.copymode(target_path, temp_path)
        except OSError:
            mask = os.umask(0)
            os.umask(mask)
            temp_path.chmod(0o666 & ~mask)

        temp_path.replace(target_path)

        if os.name == "posix":
            flags = os.O_RDONLY
            if hasattr(os, "O_DIRECTORY"):
                flags |= os.O_DIRECTORY
            dir_fd = os.open(target_path.parent, flags)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        if temp_path.exists():
            with suppress(OSError):
                temp_path.unlink()


@runtime_checkable
class WriteSink(Protocol):
    """Writes binary content to a filepath."""

    def write(self, path: Path, content: bytes) -> None:
        """Write the given binary content to the specified path."""
        ...


class FileSystemSink(WriteSink):
    """Writes files directly to the filesystem."""

    @override
    def write(self, path: Path, content: bytes) -> None:
        with atomic_write(path) as f:
            f.write(content)


class MemorySink(WriteSink):
    """Writes files into a dictionary."""

    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    @override
    def write(self, path: Path, content: bytes) -> None:
        self.files[str(path)] = content
