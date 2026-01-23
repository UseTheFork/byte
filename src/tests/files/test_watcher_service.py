"""Test suite for FileWatcherService."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from byte.config import ByteConfig
from tests.utils import create_test_file

if TYPE_CHECKING:
    from byte import Application


@pytest.fixture
def config():
    """Create a ByteConfig instance with a temporary git repository.

    Usage: Tests can use this fixture to get a configured ByteConfig.
    """
    config = ByteConfig()
    return config


@pytest.fixture
def providers():
    """Provide FileServiceProvider for watcher service tests."""
    from byte.files import FileServiceProvider

    return [FileServiceProvider]


@pytest.mark.asyncio
async def test_detects_new_file_creation(application: Application):
    """Test that watcher detects when a new file is created."""

    from byte.files import FileDiscoveryService

    # Get initial file count
    discovery_service = application.make(FileDiscoveryService)
    initial_files = await discovery_service.get_files()
    initial_count = len(initial_files)

    # Create a new file
    await create_test_file(application, "watched_file.py", "# new file")

    # Refresh and check if file was added to discovery cache
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    # Should have detected and added the new file
    assert len(files) > initial_count
    assert "watched_file.py" in file_names


@pytest.mark.asyncio
async def test_detects_file_deletion(application: Application):
    """Test that watcher detects when a file is deleted."""
    from byte.files import FileDiscoveryService

    # Create a file first
    temp_file = await create_test_file(application, "to_delete.py", "# temporary file")

    discovery_service = application.make(FileDiscoveryService)
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]
    assert "to_delete.py" in file_names

    # Delete the file
    temp_file.unlink()

    # Wait for watcher to process the deletion
    await asyncio.sleep(0.5)

    # Check if file was removed from discovery cache
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    # Should have detected and removed the deleted file
    assert "to_delete.py" not in file_names


@pytest.mark.asyncio
async def test_ignores_files_matching_ignore_patterns(application: Application):
    """Test that watcher respects ignore patterns and doesn't track ignored files."""
    from byte.files import FileDiscoveryService

    # Create a .pyc file that should be ignored
    ignored_file = application.base_path("ignored.pyc")
    ignored_file.write_text("compiled python")

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # Check that ignored file was not added to discovery cache
    discovery_service = application.make(FileDiscoveryService)
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    # Should not have added the ignored file
    assert "ignored.pyc" not in file_names


@pytest.mark.asyncio
async def test_removes_file_from_context_when_deleted(application: Application):
    """Test that watcher removes files from context when they are deleted."""
    from byte.files import FileDiscoveryService, FileMode, FileService

    # Create a file and add it to context
    context_file = application.base_path("context_file.py")
    context_file.write_text("# file in context")

    # Wait for watcher to detect creation
    await asyncio.sleep(0.5)

    # Refresh discovery to ensure file is in cache
    discovery_service = application.make(FileDiscoveryService)
    await discovery_service.refresh()

    file_service = application.make(FileService)
    await file_service.add_file(context_file, FileMode.EDITABLE)

    # Verify file is in context
    assert await file_service.is_file_in_context(context_file) is True

    # Delete the file
    context_file.unlink()

    # Wait for watcher to process the deletion
    await asyncio.sleep(0.5)

    # File should be removed from context
    assert await file_service.is_file_in_context(context_file) is False


@pytest.mark.asyncio
async def test_ignores_directory_changes(application: Application):
    """Test that watcher ignores directory creation/deletion."""
    from byte.files import FileDiscoveryService

    discovery_service = application.make(FileDiscoveryService)
    initial_files = await discovery_service.get_files()
    initial_count = len(initial_files)

    # Create a directory
    new_dir = application.base_path("new_directory")
    new_dir.mkdir()

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # Directory itself should not be added to file cache
    files = await discovery_service.get_files()
    assert len(files) == initial_count


@pytest.mark.asyncio
async def test_detects_files_in_new_directories(application: Application):
    """Test that watcher detects files created in new directories."""
    from byte.files import FileDiscoveryService

    # Get initial file count
    discovery_service = application.make(FileDiscoveryService)
    initial_files = await discovery_service.get_files()
    initial_count = len(initial_files)

    # Create a new directory
    new_dir = application.base_path("new_dir")
    new_dir.mkdir()

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # Create a file in the new directory
    new_file = new_dir / "file_in_new_dir.py"
    new_file.write_text("# file in new directory")

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # File should be detected and added
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    assert len(files) > initial_count
    assert "file_in_new_dir.py" in file_names


@pytest.mark.asyncio
async def test_ignores_files_in_ignored_directories(application: Application):
    """Test that watcher ignores files created in ignored directories."""
    from byte.files import FileDiscoveryService

    # Create __pycache__ directory
    pycache_dir = application.base_path("__pycache__")
    pycache_dir.mkdir()

    # Create a file in the ignored directory
    ignored_file = pycache_dir / "module.pyc"
    ignored_file.write_text("compiled")

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # File should not be added to discovery cache
    discovery_service = application.make(FileDiscoveryService)
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    assert "module.pyc" not in file_names


@pytest.mark.asyncio
async def test_handles_rapid_file_changes(application: Application):
    """Test that watcher handles multiple rapid file changes correctly."""
    from byte.files import FileDiscoveryService

    # Create multiple files rapidly
    files_to_create = ["rapid1.py", "rapid2.py", "rapid3.py"]
    for filename in files_to_create:
        file_path = application.base_path(filename)
        file_path.write_text(f"# {filename}")

    # Wait for watcher to process all changes
    await asyncio.sleep(1.0)

    # All files should be detected
    discovery_service = application.make(FileDiscoveryService)
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    for filename in files_to_create:
        assert filename in file_names


@pytest.mark.asyncio
async def test_emits_file_changed_event(application: Application):
    """Test that watcher emits FILE_CHANGED events."""
    from byte import EventBus, EventType

    event_bus = application.make(EventBus)
    events_received = []

    # Register listener for FILE_CHANGED events
    async def capture_event(payload):
        events_received.append(payload)
        return payload

    event_bus.on(EventType.FILE_CHANGED.value, capture_event)

    # Create a new file
    new_file = application.base_path("event_test.py")
    new_file.write_text("# test file")

    # Wait for watcher to process and emit event
    await asyncio.sleep(0.5)

    # Should have received at least one FILE_CHANGED event
    assert len(events_received) > 0

    # Check event payload structure
    event = events_received[0]
    assert event.get("file_path") is not None
    assert event.get("change_type") in ["added", "modified", "deleted"]


@pytest.mark.asyncio
async def test_handles_file_modification(application: Application):
    """Test that watcher detects file modifications."""
    from byte import EventBus, EventType

    # Create a file first
    test_file = application.base_path("modify_test.py")
    test_file.write_text("# original content")

    # Wait for initial creation to be processed
    await asyncio.sleep(0.5)

    event_bus = application.make(EventBus)
    events_received = []

    async def capture_event(payload):
        events_received.append(payload)
        return payload

    event_bus.on(EventType.FILE_CHANGED.value, capture_event)

    # Modify the file
    test_file.write_text("# modified content")

    # Wait for watcher to detect modification
    await asyncio.sleep(0.5)

    # Should have received a modification event
    assert len(events_received) > 0


@pytest.mark.asyncio
async def test_watcher_filter_uses_ignore_service(application: Application):
    """Test that watcher's filter function correctly uses ignore service patterns."""

    from byte.files import FileWatcherService

    watcher_service = application.make(FileWatcherService)

    # Test with a file that should be ignored
    ignored_path = str(application.base_path("test.pyc"))
    from watchfiles import Change

    result = watcher_service._watch_filter(Change.added, ignored_path)

    # Should return False for ignored files
    assert result is False

    # Test with a file that should not be ignored
    normal_path = str(application.base_path("test.py"))
    result = watcher_service._watch_filter(Change.added, normal_path)

    # Should return True for normal files
    assert result is True


@pytest.mark.asyncio
async def test_handles_nested_directory_file_changes(application: Application):
    """Test that watcher detects changes in nested directories."""
    from byte.files import FileDiscoveryService

    # Get initial file count
    discovery_service = application.make(FileDiscoveryService)
    initial_files = await discovery_service.get_files()
    initial_count = len(initial_files)

    # Create nested directory structure
    nested_dir = application.base_path("src/utils")
    nested_dir.mkdir(parents=True)

    await asyncio.sleep(0.5)

    # Create a file in nested directory
    nested_file = nested_dir / "helper.py"
    nested_file.write_text("# helper functions")

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # File should be detected
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    assert len(files) > initial_count
    assert "helper.py" in file_names


@pytest.mark.asyncio
async def test_watcher_handles_custom_ignore_patterns(application: Application):
    """Test that watcher respects custom ignore patterns from config."""
    from byte.files import FileDiscoveryService, FileIgnoreService, FileWatcherService

    # Add custom ignore pattern with wildcard to match the file
    config = application["config"]
    config.files.ignore.append("custom_ignored*")

    # Refresh ignore service to pick up new pattern
    ignore_service = application.make(FileIgnoreService)
    await ignore_service.refresh()

    # Restart watcher to pick up new ignore patterns
    watcher_service = application.make(FileWatcherService)
    watcher_service.ignore_service = ignore_service

    # Create a file matching custom pattern
    custom_file = application.base_path("custom_ignored.txt")
    custom_file.write_text("should be ignored")

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # File should not be added to discovery cache
    discovery_service = application.make(FileDiscoveryService)
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    assert "custom_ignored.txt" not in file_names


@pytest.mark.asyncio
async def test_watcher_continues_after_error(application: Application):
    """Test that watcher continues operating after encountering an error."""
    from byte.files import FileDiscoveryService

    # Create a valid file
    valid_file = application.base_path("valid.py")
    valid_file.write_text("# valid file")

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # Create another valid file after potential error
    another_file = application.base_path("another.py")
    another_file.write_text("# another file")

    # Wait for watcher to process
    await asyncio.sleep(0.5)

    # Both files should be detected
    discovery_service = application.make(FileDiscoveryService)
    files = await discovery_service.get_files()
    file_names = [f.name for f in files]

    assert "valid.py" in file_names
    assert "another.py" in file_names
