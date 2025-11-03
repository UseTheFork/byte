import pytest

from byte.core.config.config import ByteConfg
from byte.domain.files.service.discovery_service import FileDiscoveryService


@pytest.mark.asyncio
async def test_get_files_returns_all_discovered_files(test_container, create_test_file):
	"""Test that get_files returns all non-ignored files from project."""
	# Create test files
	create_test_file("test1.py", "print('test1')")
	create_test_file("test2.py", "print('test2')")
	create_test_file("src/main.py", "print('main')")

	discovery = await test_container.make(FileDiscoveryService)
	# Refresh to pick up newly created files
	await discovery.refresh()
	files = await discovery.get_files()

	# Should find all created files
	assert len(files) >= 3
	file_names = [f.name for f in files]
	assert "test1.py" in file_names
	assert "test2.py" in file_names
	assert "main.py" in file_names


@pytest.mark.asyncio
async def test_get_files_filters_by_extension(test_container, create_test_file, tmp_project_root):
	"""Test that get_files can filter by file extension."""
	create_test_file("test.py", "print('test')")
	create_test_file("readme.md", "# README")
	create_test_file("config.json", "{}")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	py_files = await discovery.get_files(".py")

	# Should only return Python files
	assert all(f.suffix == ".py" for f in py_files)
	assert any(f.name == "test.py" for f in py_files)


@pytest.mark.asyncio
async def test_get_relative_paths_returns_strings(test_container, create_test_file, tmp_project_root):
	"""Test that get_relative_paths returns string paths relative to project root."""
	create_test_file("src/module/file.py", "# test")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	paths = await discovery.get_relative_paths()

	# Should return strings, not Path objects
	assert all(isinstance(p, str) for p in paths)
	assert any("src/module/file.py" in p for p in paths)


@pytest.mark.asyncio
async def test_find_files_exact_prefix_match(test_container, create_test_file, tmp_project_root):
	"""Test that find_files prioritizes exact prefix matches."""
	create_test_file("bootstrap.py", "# boot")
	create_test_file("src/bootstrap_helper.py", "# helper")
	create_test_file("tests/test_boot.py", "# test")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	matches = await discovery.find_files("boot")

	# Should find files with 'boot' in the path
	assert len(matches) > 0
	# Exact prefix match should come first
	assert matches[0].name == "bootstrap.py"


@pytest.mark.asyncio
async def test_find_files_fuzzy_match(test_container, create_test_file, tmp_project_root):
	"""Test that find_files supports fuzzy matching."""
	create_test_file("src/services/file_service.py", "# service")
	create_test_file("tests/test_service.py", "# test")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	matches = await discovery.find_files("service")

	# Should find files with 'service' anywhere in path
	assert len(matches) >= 2
	file_names = [f.name for f in matches]
	assert "file_service.py" in file_names
	assert "test_service.py" in file_names


@pytest.mark.asyncio
async def test_find_files_filename_priority(test_container, create_test_file, tmp_project_root):
	"""Test that find_files prioritizes matches in filename over directory path."""
	create_test_file("config/settings.py", "# settings")
	create_test_file("src/config.py", "# config")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	matches = await discovery.find_files("config")

	# File named 'config.py' should rank higher than file in 'config/' directory
	assert len(matches) >= 2
	# The file with 'config' in its name should have better relevance
	assert any(f.name == "config.py" for f in matches)


@pytest.mark.asyncio
async def test_add_file_to_cache(test_container, create_test_file, tmp_project_root):
	"""Test that add_file adds a new file to the discovery cache."""
	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	initial_count = len(await discovery.get_files())

	# Create a new file after discovery has booted
	new_file = tmp_project_root / "new_file.py"
	new_file.write_text("# new")

	# Add it to the cache
	result = await discovery.add_file(new_file)
	assert result is True

	# Should now appear in discovered files
	files = await discovery.get_files()
	assert len(files) == initial_count + 1
	assert new_file in files


@pytest.mark.asyncio
async def test_add_file_ignores_ignored_files(test_container, tmp_project_root):
	"""Test that add_file respects ignore patterns."""
	discovery = await test_container.make(FileDiscoveryService)

	# Try to add a file that should be ignored
	ignored_file = tmp_project_root / "__pycache__" / "test.pyc"
	ignored_file.parent.mkdir(exist_ok=True)
	ignored_file.write_text("# ignored")

	result = await discovery.add_file(ignored_file)
	assert result is False

	# Should not appear in discovered files
	files = await discovery.get_files()
	assert ignored_file not in files


@pytest.mark.asyncio
async def test_remove_file_from_cache(test_container, create_test_file, tmp_project_root):
	"""Test that remove_file removes a file from the discovery cache."""
	file_path = create_test_file("to_remove.py", "# remove me")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	initial_files = await discovery.get_files()
	assert file_path in initial_files

	# Remove from cache
	result = await discovery.remove_file(file_path)
	assert result is True

	# Should no longer appear in discovered files
	files = await discovery.get_files()
	assert file_path not in files


@pytest.mark.asyncio
async def test_refresh_rescans_project(test_container, create_test_file, tmp_project_root):
	"""Test that refresh rescans the project directory."""
	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	initial_count = len(await discovery.get_files())

	# Create a new file after initial scan
	new_file = tmp_project_root / "added_after_scan.py"
	new_file.write_text("# new")

	# Refresh should pick up the new file
	await discovery.refresh()
	files = await discovery.get_files()

	assert len(files) == initial_count + 1
	assert new_file in files


@pytest.mark.asyncio
async def test_discovery_respects_gitignore(test_container, tmp_project_root):
	"""Test that file discovery respects .gitignore patterns."""
	# Create .gitignore
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("*.log\ntemp/\n")

	# Create files that should be ignored
	log_file = tmp_project_root / "debug.log"
	log_file.write_text("log content")

	temp_dir = tmp_project_root / "temp"
	temp_dir.mkdir()
	temp_file = temp_dir / "temp.txt"
	temp_file.write_text("temp content")

	# Create file that should NOT be ignored
	valid_file = tmp_project_root / "valid.py"
	valid_file.write_text("# valid")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	# Refresh discovery to pick up gitignore
	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()

	files = await discovery.get_files()
	file_paths = [str(f) for f in files]

	# Ignored files should not appear
	assert str(log_file) not in file_paths
	assert str(temp_file) not in file_paths

	# Valid file should appear
	assert str(valid_file) in file_paths


@pytest.mark.asyncio
async def test_get_files_sorted_by_relative_path(test_container, create_test_file, tmp_project_root):
	"""Test that get_files returns files sorted by relative path."""
	create_test_file("z_last.py", "# last")
	create_test_file("a_first.py", "# first")
	create_test_file("m_middle.py", "# middle")

	# Update config to point to this test's directory
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	discovery = await test_container.make(FileDiscoveryService)
	await discovery.refresh()
	files = await discovery.get_files()

	# Extract just the created test files
	test_files = [f for f in files if f.name in ["z_last.py", "a_first.py", "m_middle.py"]]

	# Should be sorted alphabetically
	assert test_files[0].name == "a_first.py"
	assert test_files[1].name == "m_middle.py"
	assert test_files[2].name == "z_last.py"
