from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from byte import Application


async def do_pause(delay: float = 0.5):
    """ """
    import asyncio

    await asyncio.sleep(delay)


async def create_test_file(application: Application, file_path: str, content: str) -> Path:
    """Create a test file with content and pause for file watcher processing.

    Usage: `await self.create_test_file(application, "test.py", "print('hello')")`
    """

    new_file = application.root_path(file_path)
    new_file.write_text(content)
    await do_pause()
    return new_file
