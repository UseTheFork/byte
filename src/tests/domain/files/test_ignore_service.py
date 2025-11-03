import pytest

from byte.core.config.config import ByteConfg
from byte.domain.files.service.ignore_service import FileIgnoreService


@pytest.mark.asyncio
async def test_is_ignored_with_gitignore_patterns(test_container, tmp_project_root):
	"""Test that is_ignored respects .gitignore patterns."""
	# Create .gitignore with common patterns
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("*.log\n__pycache__/\n.env\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Test file patterns
	log_file = tmp_project_root / "debug.log"
	assert await ignore_service.is_ignored(log_file) is True

	# Test directory patterns
	pycache_file = tmp_project_root / "__pycache__" / "module.pyc"
	assert await ignore_service.is_ignored(pycache_file) is True

	# Test non-ignored file
	valid_file = tmp_project_root / "main.py"
	assert await ignore_service.is_ignored(valid_file) is False


@pytest.mark.asyncio
async def test_is_ignored_with_config_patterns(test_container, tmp_project_root):
	"""Test that is_ignored respects configuration ignore patterns."""
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root
	# Config has default ignore patterns like .byte/cache, .ruff_cache, etc.

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Test default config patterns
	byte_cache = tmp_project_root / ".byte" / "cache" / "file.txt"
	assert await ignore_service.is_ignored(byte_cache) is True

	ruff_cache = tmp_project_root / ".ruff_cache" / "file.txt"
	assert await ignore_service.is_ignored(ruff_cache) is True

	node_modules = tmp_project_root / "node_modules" / "package" / "index.js"
	assert await ignore_service.is_ignored(node_modules) is True


@pytest.mark.asyncio
async def test_is_ignored_combines_gitignore_and_config(test_container, tmp_project_root):
	"""Test that is_ignored combines both .gitignore and config patterns."""
	# Create .gitignore
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("*.log\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Test gitignore pattern
	log_file = tmp_project_root / "app.log"
	assert await ignore_service.is_ignored(log_file) is True

	# Test config pattern
	pycache = tmp_project_root / "__pycache__" / "module.pyc"
	assert await ignore_service.is_ignored(pycache) is True


@pytest.mark.asyncio
async def test_is_ignored_with_nested_directories(test_container, tmp_project_root):
	"""Test that is_ignored handles nested directory patterns correctly."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("build/\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Files in ignored directory should be ignored
	build_file = tmp_project_root / "build" / "output.txt"
	assert await ignore_service.is_ignored(build_file) is True

	# Nested files in ignored directory should also be ignored
	nested_build = tmp_project_root / "build" / "nested" / "deep" / "file.txt"
	assert await ignore_service.is_ignored(nested_build) is True


@pytest.mark.asyncio
async def test_is_ignored_with_wildcard_patterns(test_container, tmp_project_root):
	"""Test that is_ignored handles wildcard patterns correctly."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("*.pyc\ntest_*.py\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Test extension wildcard
	pyc_file = tmp_project_root / "module.pyc"
	assert await ignore_service.is_ignored(pyc_file) is True

	# Test prefix wildcard
	test_file = tmp_project_root / "test_main.py"
	assert await ignore_service.is_ignored(test_file) is True

	# Non-matching file should not be ignored
	main_file = tmp_project_root / "main.py"
	assert await ignore_service.is_ignored(main_file) is False


@pytest.mark.asyncio
async def test_is_ignored_outside_project_root(test_container, tmp_project_root):
	"""Test that files outside project root are considered ignored."""
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)

	# File outside project root (using parent of tmp_project_root)
	outside_file = tmp_project_root.parent.parent / "outside" / "file.txt"
	assert await ignore_service.is_ignored(outside_file) is True


@pytest.mark.asyncio
async def test_is_ignored_with_comments_in_gitignore(test_container, tmp_project_root):
	"""Test that is_ignored handles comments in .gitignore correctly."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("# This is a comment\n*.log\n# Another comment\n__pycache__/\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Patterns should work despite comments
	log_file = tmp_project_root / "app.log"
	assert await ignore_service.is_ignored(log_file) is True

	pycache = tmp_project_root / "__pycache__" / "module.pyc"
	assert await ignore_service.is_ignored(pycache) is True


@pytest.mark.asyncio
async def test_is_ignored_with_empty_gitignore(test_container, tmp_project_root):
	"""Test that is_ignored works with empty .gitignore."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Should still respect config patterns
	pycache = tmp_project_root / "__pycache__" / "module.pyc"
	assert await ignore_service.is_ignored(pycache) is True

	# Regular files should not be ignored
	regular_file = tmp_project_root / "main.py"
	assert await ignore_service.is_ignored(regular_file) is False


@pytest.mark.asyncio
async def test_is_ignored_without_gitignore(test_container, tmp_project_root):
	"""Test that is_ignored works when .gitignore doesn't exist."""
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Should still respect config patterns
	pycache = tmp_project_root / "__pycache__" / "module.pyc"
	assert await ignore_service.is_ignored(pycache) is True

	# Regular files should not be ignored
	regular_file = tmp_project_root / "main.py"
	assert await ignore_service.is_ignored(regular_file) is False


@pytest.mark.asyncio
async def test_refresh_reloads_patterns(test_container, tmp_project_root):
	"""Test that refresh reloads ignore patterns from filesystem."""
	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Initially, .log files are not ignored
	log_file = tmp_project_root / "app.log"
	assert await ignore_service.is_ignored(log_file) is False

	# Add .gitignore with new pattern
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("*.log\n")

	# Refresh to pick up new patterns
	await ignore_service.refresh()

	# Now .log files should be ignored
	assert await ignore_service.is_ignored(log_file) is True


@pytest.mark.asyncio
async def test_get_pathspec_returns_compiled_spec(test_container, tmp_project_root):
	"""Test that get_pathspec returns the compiled pathspec."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("*.log\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	pathspec = ignore_service.get_pathspec()
	assert pathspec is not None

	# Verify pathspec works correctly
	assert pathspec.match_file("app.log") is True
	assert pathspec.match_file("main.py") is False


@pytest.mark.asyncio
async def test_is_ignored_with_parent_directory_patterns(test_container, tmp_project_root):
	"""Test that is_ignored checks parent directories for ignore patterns."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("__pycache__/\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# File inside ignored directory should be ignored
	pycache_file = tmp_project_root / "src" / "__pycache__" / "module.pyc"
	assert await ignore_service.is_ignored(pycache_file) is True

	# Deeply nested file in ignored directory should be ignored
	deep_file = tmp_project_root / "src" / "nested" / "__pycache__" / "deep" / "file.pyc"
	assert await ignore_service.is_ignored(deep_file) is True


@pytest.mark.asyncio
async def test_is_ignored_with_negation_patterns(test_container, tmp_project_root):
	"""Test that is_ignored handles negation patterns correctly."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("*.log\n!important.log\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Regular .log files should be ignored
	regular_log = tmp_project_root / "app.log"
	assert await ignore_service.is_ignored(regular_log) is True

	# Negated file should not be ignored
	important_log = tmp_project_root / "important.log"
	assert await ignore_service.is_ignored(important_log) is False


@pytest.mark.asyncio
async def test_is_ignored_with_directory_specific_patterns(test_container, tmp_project_root):
	"""Test that is_ignored handles directory-specific patterns."""
	gitignore = tmp_project_root / ".gitignore"
	gitignore.write_text("docs/*.txt\n")

	config = await test_container.make(ByteConfg)
	config.project_root = tmp_project_root

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# File in docs/ should be ignored
	docs_txt = tmp_project_root / "docs" / "readme.txt"
	assert await ignore_service.is_ignored(docs_txt) is True

	# File in other directory should not be ignored
	other_txt = tmp_project_root / "src" / "readme.txt"
	assert await ignore_service.is_ignored(other_txt) is False


@pytest.mark.asyncio
async def test_is_ignored_with_no_project_root(test_container):
	"""Test that is_ignored returns False when no project root is configured."""
	config = await test_container.make(ByteConfg)
	config.project_root = None

	ignore_service = await test_container.make(FileIgnoreService)
	await ignore_service.refresh()

	# Should return False for any path when no project root
	from pathlib import Path

	result = await ignore_service.is_ignored(Path("/some/path/file.py"))
	assert result is False
