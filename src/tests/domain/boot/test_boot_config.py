import pytest

from byte.bootstrap import bootstrap, shutdown
from byte.core.config.config import ByteConfig
from byte.domain.files.models import FileMode
from byte.domain.files.service.file_service import FileService
from byte.main import Byte


@pytest.mark.asyncio
async def test_boot_config_empty_lists(test_config: ByteConfig):
    """Test that empty boot config lists don't cause errors."""
    # Set empty boot config (default state)
    test_config.boot.read_only_files = []
    test_config.boot.editable_files = []

    # Bootstrap container and initialize app
    container = await bootstrap(test_config)
    try:
        app = Byte(container)
        await app.initialize()

        # Verify no files in context
        file_service = await container.make(FileService)
        assert len(file_service.list_files()) == 0
    finally:
        # Cleanup
        await shutdown(container)


@pytest.mark.asyncio
async def test_boot_config_read_only_files(test_config: ByteConfig, create_test_file):
    """Test that --read-only flag adds files to read-only context."""
    # Create test files
    test_file1 = create_test_file("test1.py", "# Test file 1")
    test_file2 = create_test_file("test2.py", "# Test file 2")

    # Set boot config with read-only files
    test_config.boot.read_only_files = [str(test_file1), str(test_file2)]
    test_config.boot.editable_files = []

    # Bootstrap container and initialize app
    container = await bootstrap(test_config)
    try:
        app = Byte(container)
        await app.initialize()

        # Verify files are in context with READ_ONLY mode
        file_service = await container.make(FileService)
        files = file_service.list_files()
        assert len(files) == 2

        file1 = file_service.get_file_context(str(test_file1))
        assert file1 is not None
        assert file1.mode == FileMode.READ_ONLY

        file2 = file_service.get_file_context(str(test_file2))
        assert file2 is not None
        assert file2.mode == FileMode.READ_ONLY
    finally:
        # Cleanup
        await shutdown(container)


@pytest.mark.asyncio
async def test_boot_config_editable_files(test_config: ByteConfig, create_test_file):
    """Test that --add flag adds files to editable context."""
    # Create test files
    test_file1 = create_test_file("src/main.py", "# Main file")
    test_file2 = create_test_file("src/utils.py", "# Utils file")

    # Set boot config with editable files
    test_config.boot.read_only_files = []
    test_config.boot.editable_files = [str(test_file1), str(test_file2)]

    # Bootstrap container and initialize app
    container = await bootstrap(test_config)
    try:
        app = Byte(container)
        await app.initialize()

        # Verify files are in context with EDITABLE mode
        file_service = await container.make(FileService)
        files = file_service.list_files()
        assert len(files) == 2

        file1 = file_service.get_file_context(str(test_file1))
        assert file1 is not None
        assert file1.mode == FileMode.EDITABLE

        file2 = file_service.get_file_context(str(test_file2))
        assert file2 is not None
        assert file2.mode == FileMode.EDITABLE
    finally:
        # Cleanup
        await shutdown(container)


@pytest.mark.asyncio
async def test_boot_config_mixed_files(test_config: ByteConfig, create_test_file):
    """Test that both --read-only and --add flags work together."""
    # Create test files
    readonly_file = create_test_file("README.md", "# README")
    editable_file = create_test_file("src/app.py", "# App file")

    # Set boot config with both read-only and editable files
    test_config.boot.read_only_files = [str(readonly_file)]
    test_config.boot.editable_files = [str(editable_file)]

    # Bootstrap container and initialize app
    container = await bootstrap(test_config)
    try:
        app = Byte(container)
        await app.initialize()

        # Verify files are in context with correct modes
        file_service = await container.make(FileService)
        files = file_service.list_files()
        assert len(files) == 2

        ro_file = file_service.get_file_context(str(readonly_file))
        assert ro_file is not None
        assert ro_file.mode == FileMode.READ_ONLY

        edit_file = file_service.get_file_context(str(editable_file))
        assert edit_file is not None
        assert edit_file.mode == FileMode.EDITABLE
    finally:
        # Cleanup
        await shutdown(container)
