import pytest

from byte.core.config.config import ByteConfig
from byte.domain.files.models import FileMode
from byte.domain.files.service.discovery_service import FileDiscoveryService
from byte.domain.files.service.file_service import FileService


@pytest.mark.asyncio
async def test_add_single_file_to_context(test_container, create_test_file, tmp_project_root):
    """Test adding a single file to the context."""
    file_path = create_test_file("test.py", "print('test')")

    # Update config and refresh discovery
    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    result = await file_service.add_file(file_path, FileMode.EDITABLE)

    assert result is True
    assert await file_service.is_file_in_context(file_path)


@pytest.mark.asyncio
async def test_add_file_with_glob_pattern(test_container, create_test_file, tmp_project_root):
    """Test adding multiple files using glob pattern."""
    test1_path = create_test_file("test1.py", "# test1")
    test2_path = create_test_file("test2.py", "# test2")
    readme_path = create_test_file("readme.md", "# README")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    result = await file_service.add_file(str(tmp_project_root / "*.py"), FileMode.EDITABLE)

    assert result is True
    assert await file_service.is_file_in_context(test1_path)
    assert await file_service.is_file_in_context(test2_path)
    assert not await file_service.is_file_in_context(readme_path)


@pytest.mark.asyncio
async def test_add_file_not_in_discovery(test_container, tmp_project_root):
    """Test that adding a file not in discovery service fails."""
    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    file_service = await test_container.make(FileService)
    result = await file_service.add_file("nonexistent.py", FileMode.EDITABLE)

    assert result is False


@pytest.mark.asyncio
async def test_add_duplicate_file_returns_false(test_container, create_test_file, tmp_project_root):
    """Test that adding the same file twice returns False."""
    file_path = create_test_file("test.py", "# test")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)

    # First add should succeed
    result1 = await file_service.add_file(file_path, FileMode.EDITABLE)
    assert result1 is True

    # Second add should fail
    result2 = await file_service.add_file(file_path, FileMode.EDITABLE)
    assert result2 is False


@pytest.mark.asyncio
async def test_remove_file_from_context(test_container, create_test_file, tmp_project_root):
    """Test removing a file from context."""
    file_path = create_test_file("test.py", "# test")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(file_path, FileMode.EDITABLE)

    result = await file_service.remove_file(file_path)
    assert result is True
    assert not await file_service.is_file_in_context(file_path)


@pytest.mark.asyncio
async def test_remove_file_with_glob_pattern(test_container, create_test_file, tmp_project_root):
    """Test removing multiple files using glob pattern."""
    test1_path = create_test_file("test1.py", "# test1")
    test2_path = create_test_file("test2.py", "# test2")
    readme_path = create_test_file("readme.md", "# README")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(str(tmp_project_root / "*.py"), FileMode.EDITABLE)
    await file_service.add_file(readme_path, FileMode.READ_ONLY)

    result = await file_service.remove_file(str(tmp_project_root / "*.py"))
    assert result is True
    assert not await file_service.is_file_in_context(test1_path)
    assert not await file_service.is_file_in_context(test2_path)
    assert await file_service.is_file_in_context(readme_path)


@pytest.mark.asyncio
async def test_remove_nonexistent_file_returns_false(test_container, tmp_project_root):
    """Test that removing a file not in context returns False."""
    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    file_service = await test_container.make(FileService)
    result = await file_service.remove_file("nonexistent.py")

    assert result is False


@pytest.mark.asyncio
async def test_list_files_all(test_container, create_test_file, tmp_project_root):
    """Test listing all files in context."""
    test1_path = create_test_file("test1.py", "# test1")
    test2_path = create_test_file("test2.py", "# test2")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(test1_path, FileMode.EDITABLE)
    await file_service.add_file(test2_path, FileMode.READ_ONLY)

    all_files = file_service.list_files()
    assert len(all_files) == 2


@pytest.mark.asyncio
async def test_list_files_by_mode(test_container, create_test_file, tmp_project_root):
    """Test listing files filtered by mode."""
    editable_path = create_test_file("editable.py", "# editable")
    readonly_path = create_test_file("readonly.py", "# readonly")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(editable_path, FileMode.EDITABLE)
    await file_service.add_file(readonly_path, FileMode.READ_ONLY)

    editable_files = file_service.list_files(FileMode.EDITABLE)
    readonly_files = file_service.list_files(FileMode.READ_ONLY)

    assert len(editable_files) == 1
    assert len(readonly_files) == 1
    assert editable_files[0].path.name == "editable.py"
    assert readonly_files[0].path.name == "readonly.py"


@pytest.mark.asyncio
async def test_list_files_sorted_by_relative_path(test_container, create_test_file, tmp_project_root):
    """Test that list_files returns files sorted by relative path."""
    create_test_file("z_last.py", "# last")
    create_test_file("a_first.py", "# first")
    create_test_file("m_middle.py", "# middle")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(str(tmp_project_root / "*.py"), FileMode.EDITABLE)

    files = file_service.list_files()
    file_names = [f.path.name for f in files]

    assert file_names[0] == "a_first.py"
    assert file_names[1] == "m_middle.py"
    assert file_names[2] == "z_last.py"


@pytest.mark.asyncio
async def test_get_file_context(test_container, create_test_file, tmp_project_root):
    """Test retrieving file context metadata."""
    file_path = create_test_file("test.py", "# test")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(file_path, FileMode.EDITABLE)

    context = file_service.get_file_context(file_path)
    assert context is not None
    assert context.mode == FileMode.EDITABLE
    assert context.path.name == "test.py"


@pytest.mark.asyncio
async def test_get_file_context_nonexistent(test_container, tmp_project_root):
    """Test that getting context for nonexistent file returns None."""
    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    file_service = await test_container.make(FileService)
    context = file_service.get_file_context("nonexistent.py")

    assert context is None


@pytest.mark.asyncio
async def test_is_file_in_context(test_container, create_test_file, tmp_project_root):
    """Test checking if a file is in context."""
    file_path = create_test_file("test.py", "# test")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)

    assert not await file_service.is_file_in_context(file_path)

    await file_service.add_file(file_path, FileMode.EDITABLE)
    assert await file_service.is_file_in_context(file_path)


@pytest.mark.asyncio
async def test_clear_context(test_container, create_test_file, tmp_project_root):
    """Test clearing all files from context."""
    create_test_file("test1.py", "# test1")
    create_test_file("test2.py", "# test2")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(str(tmp_project_root / "*.py"), FileMode.EDITABLE)

    assert len(file_service.list_files()) == 2

    await file_service.clear_context()
    assert len(file_service.list_files()) == 0


@pytest.mark.asyncio
async def test_generate_context_prompt(test_container, create_test_file, tmp_project_root):
    """Test generating context prompt with file contents."""
    editable_path = create_test_file("editable.py", "print('editable')")
    readonly_path = create_test_file("readonly.py", "print('readonly')")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(editable_path, FileMode.EDITABLE)
    await file_service.add_file(readonly_path, FileMode.READ_ONLY)

    read_only, editable = await file_service.generate_context_prompt()

    assert len(read_only) == 1
    assert len(editable) == 1
    assert "readonly.py" in read_only[0]
    assert "mode=read-only" in read_only[0]
    assert "editable.py" in editable[0]
    assert "mode=editable" in editable[0]


@pytest.mark.asyncio
async def test_generate_context_prompt_empty(test_container, tmp_project_root):
    """Test generating context prompt with no files."""
    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    file_service = await test_container.make(FileService)
    read_only, editable = await file_service.generate_context_prompt()

    assert len(read_only) == 0
    assert len(editable) == 0


@pytest.mark.asyncio
async def test_find_project_files(test_container, create_test_file, tmp_project_root):
    """Test finding project files by pattern."""
    create_test_file("bootstrap.py", "# boot")
    create_test_file("src/bootstrap_helper.py", "# helper")
    create_test_file("tests/test_boot.py", "# test")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    matches = await file_service.find_project_files("boot")

    assert len(matches) > 0
    assert any("bootstrap.py" in m for m in matches)


@pytest.mark.asyncio
async def test_get_project_files(test_container, create_test_file, tmp_project_root):
    """Test getting all project files."""
    create_test_file("test.py", "# test")
    create_test_file("readme.md", "# README")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    all_files = await file_service.get_project_files()
    py_files = await file_service.get_project_files(".py")

    assert len(all_files) >= 2
    assert all(isinstance(f, str) for f in all_files)
    assert len(py_files) >= 1
    assert all(f.endswith(".py") for f in py_files)


@pytest.mark.asyncio
async def test_generate_project_hierarchy(test_container, create_test_file, tmp_project_root):
    """Test generating project hierarchy structure."""
    create_test_file("readme.md", "# README")
    create_test_file("src/main.py", "# main")
    create_test_file("src/utils.py", "# utils")
    create_test_file("tests/test_main.py", "# test")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    hierarchy = await file_service.generate_project_hierarchy()

    assert "Project Structure:" in hierarchy
    assert "readme.md" in hierarchy
    assert "src/" in hierarchy
    assert "tests/" in hierarchy


@pytest.mark.asyncio
async def test_generate_context_prompt_with_line_numbers(test_container, create_test_file, tmp_project_root):
    """Test generating context prompt with line numbers."""
    file_path = create_test_file("test.py", "line1\nline2\nline3")

    config = await test_container.make(ByteConfig)
    config.project_root = tmp_project_root

    discovery = await test_container.make(FileDiscoveryService)
    await discovery.refresh()

    file_service = await test_container.make(FileService)
    await file_service.add_file(file_path, FileMode.EDITABLE)

    _, editable = await file_service.generate_context_prompt_with_line_numbers()

    assert len(editable) == 1
    assert "   1 | line1" in editable[0]
    assert "   2 | line2" in editable[0]
    assert "   3 | line3" in editable[0]
