import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from byte.domain.prompt_format.service.edit_block_service import EditBlockService

from byte.bootstrap import bootstrap
from byte.container import Container
from byte.core.config.config import ByteConfig
from byte.domain.files.service.file_service import FileService
from byte.domain.prompt_format.service.shell_command_service import ShellCommandService


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session.

    Usage: Automatically used by pytest-asyncio for async tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tmp_project_root(tmp_path: Path) -> Path:
    """Create a temporary project root directory with git initialization.

    Usage: `def test_something(tmp_project_root): ...`
    """
    # Initialize a git repository in the temp directory
    import git

    git.Repo.init(tmp_path)

    return tmp_path


@pytest_asyncio.fixture
async def test_config(tmp_project_root: Path) -> ByteConfig:
    """Create a test configuration with temporary paths.

    Usage: `async def test_something(test_config): ...`
    """
    # Create .byte directory
    byte_dir = tmp_project_root / ".byte"
    byte_dir.mkdir(exist_ok=True)

    # Create a minimal config file
    config_file = byte_dir / "config.yaml"
    config_file.write_text("model: sonnet\n")

    # Create config instance with test paths
    config = ByteConfig()
    config.project_root = tmp_project_root
    config.byte_dir = byte_dir

    return config


@pytest_asyncio.fixture
async def test_container(test_config: ByteConfig) -> AsyncGenerator[Container, None]:
    """Bootstrap a test container with minimal service configuration.

    Provides a fully configured container for testing services in isolation
    or integration. Automatically handles cleanup after tests.

    Usage: `async def test_something(test_container): service = await test_container.make(MyService)`
    """
    from byte.bootstrap import shutdown
    from byte.container import app

    # Reset the global container before each test to ensure isolation
    app.reset()

    container = await bootstrap(test_config)

    yield container

    # Cleanup: shutdown all services and reset container
    await shutdown(container)


@pytest_asyncio.fixture
async def edit_format_service(test_container: Container, tmp_project_root: Path) -> EditBlockService:
    """Provide an initialized EditBlockService instance.

    Usage: `async def test_something(edit_format_service: EditBlockService):`
    """
    service = await test_container.make(EditBlockService)
    return service


@pytest_asyncio.fixture
async def shell_command_service(test_container: Container, tmp_project_root: Path) -> ShellCommandService:
    """Provide an initialized ShellCommandService instance.

    Usage: `async def test_something(shell_command_service: ShellCommandService):`
    """
    service = await test_container.make(ShellCommandService)
    return service


@pytest_asyncio.fixture
async def file_service(test_container: Container) -> FileService:
    """Provide a fully booted FileService instance for testing.

    Usage: `async def test_something(file_service): await file_service.add_file("test.py")`
    """
    service = await test_container.make(FileService)
    return service


@pytest.fixture
def sample_file_content() -> str:
    """Provide sample Python file content for testing.

    Usage: `def test_something(sample_file_content): ...`
    """
    return '''import sys
from rich.pretty import pprint
def dump(*args, **kwargs):
	"""Debug function that pretty prints variables using rich.

	Usage:
	dump(variable1, variable2)
	dump(locals())
	dump(globals())
	"""
	if not args and not kwargs:
		# If no arguments, dump the caller's locals
		import inspect

		frame = inspect.currentframe().f_back
		pprint(frame.f_locals)
	else:
		# Print each argument
		for arg in args:
			pprint(arg)

		# Print keyword arguments
		if kwargs:
			pprint(kwargs)
'''


@pytest.fixture
def create_test_file(tmp_project_root: Path):
    """Factory fixture for creating test files with content.

    Usage: `def test_something(create_test_file): create_test_file("test.py", "content")`
    """

    def _create_file(relative_path: str, content: str) -> Path:
        file_path = tmp_project_root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_file
